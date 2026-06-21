from typing import List, Dict, Optional
from pathlib import Path
import os
from firecrawl import FirecrawlApp
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from fastembed import TextEmbedding
import uuid
from datetime import datetime
import time
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import edge_tts
import asyncio
import tempfile


load_dotenv()

def init_session_state():
    defaults = {
        "initialized":False,
        "qdrant_url": "",
        "qdrant_api_key": "",
        "firecrawl_api_key": "",
        "huggingface_api_key": "",
        "doc_url":"",
        "setup_complete": False,
        "client":None,
        "embedding_model":None,
        "selected_voice":"en-US-AriaNeural"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def sidebar_config():
    with st.sidebar:
       st.title("Configuartion")
       st.markdown("---")

       st.session_state.qdrant_url = st.text_input(
           "Qdrant URL",
           value=st.session_state.qdrant_url,
           type="password"
       )

       st.session_state.qdrant_api_key = st.text_input(
           "Qdrant API Key",
           value=st.session_state.qdrant_api_key,
           type="password"
       )

       st.session_state.firecrawl_api_key = st.text_input(
           "Firecrawl API Key",
           value=st.session_state.firecrawl_api_key,
           type="password"

       )

       st.session_state.huggingface_api_key = st.text_input(
           "Hugging Face API Key",
           value=st.session_state.huggingface_api_key,
           type="password"
       )

       st.markdown("---")
       st.session_state.doc_url = st.text_input(
           "Documentation URL",
           value=st.session_state.doc_url,
           placeholder="https://docs.example.com"
       )

       st.markdown("---")
       st.markdown("### Voice Settings")
       voices = ["en-US-AriaNeural", "en-US-GuyNeural", "en-US-JennyNeural", "en-GB-SoniaNeural", "en-GB-RyanNeural"]
       st.session_state.selected_voice = st.selectbox(
           "Select Voice",
           options = voices,
           index=voices.index(st.session_state.selected_voice),
           help="Choose the voice for the audio response"
       )

       if st.button("Initialize System", type="primary"):
           if all([
               st.session_state.qdrant_url,
               st.session_state.qdrant_api_key,
               st.session_state.firecrawl_api_key,
               st.session_state.huggingface_api_key,
               st.session_state.doc_url
           ]):
               
               progress_placeholder = st.empty()
               with progress_placeholder.container():
                   try:
                       st.markdown("Setting up Qdrant connection...")
                       client, embedding_model = setup_qdrant_collection(
                           st.session_state.qdrant_url,
                           st.session_state.qdrant_api_key


                       )
                       st.session_state.client = client
                       st.session_state.embedding_model = embedding_model
                       st.markdown("Qdrant setup complete!")

                       st.markdown("Crawling documentation pages...")
                       pages = crawl_documentation(
                           st.session_state.firecrawl_api_key,
                           st.session_state.doc_url
                       )
                       st.markdown(f"Crawl {len(pages)} documentation pages!")

                       store_embeddings(
                           client,
                           embedding_model,
                           pages,
                           "docs_embeddings"

                       )

                       st.session_state.setup_complete = True
                       st.success("System initialized successfully!")

                   except Exception as e:
                       st.error(f"Error during setup: {str(e)}")

           else:
               st.error("Please fill in all the required fields!")  

def setup_qdrant_collection(qdrant_url: str,qdrant_api_key: str, collection_name: str = "docs_embeddings"):
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    embedding_model = TextEmbedding()
    test_embedding = list(embedding_model.embed(["test"]))

    if not test_embedding:
        raise Exception("Embedding model failed")
    
    test_embedding = test_embedding[0]
    embedding_dim = len(test_embedding)

    try:
        client.create_collection(

            collection_name = collection_name,
            vectors_config = VectorParams(size=embedding_dim, distance=Distance.COSINE)
            
        )
    except Exception as e:
        if "already exists" not in str(e):
            raise e
        
    return client, embedding_model


def crawl_documentation(firecrawl_api_key: str, url: str, output_dir: Optional[str]= None):
    firecrawl = FirecrawlApp(api_key=firecrawl_api_key)
    pages = []

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    response = firecrawl.scrape_url(url)

    content = response.markdown if hasattr(response, 'markdown') else (response.html if hasattr(response, 'html') else '')
    metadata = response.metadata if hasattr(response, 'metadata') else None
    source_url = metadata.sourceURL if metadata and hasattr(metadata, 'sourceURL') else url

    if output_dir and content:
        filename= f"{uuid.uuid4()}.md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    pages.append({
        "content": content,
        "url": source_url,
        "metadata": {
            "title": metadata.title if metadata and hasattr(metadata, 'title') else '',
            "description": metadata.description if metadata and hasattr(metadata, 'description') else '',
            "language": metadata.language if metadata and hasattr(metadata, 'language') else 'en',
            "crawl_date": datetime.now().isoformat()
        }
    })

    return pages

def store_embeddings(client: QdrantClient, embedding_model: TextEmbedding, pages: List[Dict],collection_name:str):
    for page in pages:
        embedding = list(embedding_model.embed([page["content"]]))[0]
        client.upsert(
            collection_name = collection_name,
            points=[

                models.PointStruct(
                    id = str(uuid.uuid4()),

                    vector=embedding.tolist(),
                    payload={
                        "content":page["content"],
                        "url":page["url"],
                        **page["metadata"]
                    }
                )
            ]
        )

async def process_query(
        query: str,
        client: QdrantClient,
        embedding_model: TextEmbedding,
        collection_name: str,
        huggingface_api_key: str,
        selected_voice: str
):

        try:
            query_embedding = list(embedding_model.embed([query]))[0]
            search_response = client.query_points(
                collection_name = collection_name,
                query=query_embedding.tolist(),
                limit=3,
                with_payload=True
            )

            search_results = search_response.points if hasattr(search_response, 'points') else []

            if not search_results:
                raise Exception("No relevant documents found in the vector database")

            # Build context from documentation
            context = "Based on the following documentation:\n\n"
            sources = []
            for result in search_results:
                payload = result.payload
                if not payload:
                    continue
                url = payload.get('url', 'Unknown URL')
                content = payload.get('content','')
                sources.append(url)
                context += f"From {url}:\n{content[:1000]}...\n\n"

            context += f"\nUser Question: {query}"
            context += "\n\nPlease provide a clear, concise answer based on the documentation above."

            # Call Hugging Face Inference Client
            try:
                client = InferenceClient(token=huggingface_api_key)
                model_id = "mistralai/Mistral-7B-Instruct-v0.2"

                prompt = f"[INST] {context} [/INST]"
                response = client.text_generation(
                    prompt,
                    model=model_id,
                    max_new_tokens=512,
                    temperature=0.7,
                    return_full_text=False
                )

                text_response = response
            except Exception as e:
                # Fallback: return raw documentation content if API fails
                text_response = f"Based on the documentation, here's what I found about '{query}':\n\n"
                for result in search_results:
                    payload = result.payload
                    if not payload:
                        continue
                    url = payload.get('url', 'Unknown URL')
                    content = payload.get('content','')
                    text_response += f"From {url}:\n{content[:800]}...\n\n"
                text_response += "\n(Note: AI processing unavailable - showing raw documentation content)"

            # Generate audio using edge-tts
            try:
                communicate = edge_tts.Communicate(text_response, selected_voice)
                temp_dir = tempfile.gettempdir()
                audio_path = os.path.join(temp_dir, f"response_{uuid.uuid4()}.mp3")
                await communicate.save(audio_path)
            except Exception as e:
                audio_path = None

            return{
                "status":"success",
                "text_response":text_response,
                "audio_path":audio_path,
                "source":sources,
                "query_details":{
                    "vector_size":len(query_embedding),
                    "results_found":len(search_results),
                    "collection_name": collection_name
                }
            }

        except Exception as e:
            return{
                "status":"error",
                "error":str(e),
                "query": query
            }
        
def run_streamlit():
    st.set_page_config(
        page_title = "Customer Support Voice Agent",
        page_icon="🎙️",
        layout = "wide"
    )
        
    init_session_state()
    sidebar_config()

    st.title("🎙️ Customer Support Voice Agent")
    st.markdown("""
    Get AI-powered answers to your documentation questions using Hugging Face! Simply:
    1. Configure your API keys in the sidebar
    2. Enter the documentation URL you want to learn about or have questions about
    3. Ask your question below and get text responses
    """)

    query = st.text_input(
        "what would you like to know about the documentation?",
         placeholder="e.g., How do I authenticate API requests?",
         disabled = not st.session_state.setup_complete
    )

    if query and st.session_state.setup_complete:
        with st.status("Processing your query...", expanded=True) as status:
            try:
                st.markdown("Searching documentation and generating response...")
                result = asyncio.run(process_query(
                    query,
                    st.session_state.client,
                    st.session_state.embedding_model,
                    "docs_embeddings",
                    st.session_state.huggingface_api_key,
                    st.session_state.selected_voice
                ))

                if result["status"] == "success":
                    status.update(label="Query processed!", state="complete")

                    st.markdown("### Response:")
                    st.write(result["text_response"])

                    if result.get("audio_path"):
                        st.markdown(f"### Audio Response (Voice: {st.session_state.selected_voice})")
                        st.audio(result["audio_path"])

                        with open(result["audio_path"], "rb") as audio_file:
                            audio_bytes = audio_file.read()
                            st.download_button(
                                label="Download Audio Response",
                                data=audio_bytes,
                                file_name=f"voice_response_{st.session_state.selected_voice}.mp3",
                                mime="audio/mp3"
                            )

                    st.markdown("### Source:")
                    for source in result["source"]:
                        st.markdown(f"-{source}")

                else:
                    status.update(label="Error processing query",state="error")
                    st.error(f"Error:{result.get('error','Unknown error occured')}")

            except Exception as e:

                status.update(label="Error processing query", state="error")
                st.error(f"Error processing query: {str(e)}")


    elif not st.session_state.setup_complete:
        st.info("Please configure the system using the sidebar first!")

if __name__ == "__main__":
   run_streamlit()
    




  
        










