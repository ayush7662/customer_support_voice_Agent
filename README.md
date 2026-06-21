# 🎙️ Customer Support Voice Agent with OpenAI Agents SDK

Build an intelligent voice-enabled customer support agent that can answer questions from your documentation using Retrieval-Augmented Generation (RAG), GPT-4o, and HuggingFace latest Text-to-Speech models.

This project demonstrates how to create a production-ready Voice AI system that crawls documentation websites, builds a searchable knowledge base, retrieves relevant information, and responds to users through both text and natural-sounding voice.


### LIve URL: https://customer-support-voice-agent-vx2c.onrender.com

## Overview

Voice is one of the most natural and accessible ways for users to interact with applications, making it particularly valuable for customer support experiences. However, building a voice agent capable of understanding and retrieving information from a knowledge base often requires integrating multiple technologies and services.

In this tutorial, you'll learn how to build a Customer Support Voice Agent using HuggingFace Agents SDK, combining advanced language understanding, vector search, and real-time speech synthesis into a single application.

## Technologies Used

This project leverages the following tools and services:

* **HuggingFace mistralai/Mistral-7B-Instruct-v0.2** – Generates accurate, context-aware responses.
* **HuggingFace edge_tts   TTS** – Converts responses into natural-sounding speech.
* **HuggingFaceAgents SDK** – Orchestrates agents and manages the voice pipeline.
* **Firecrawl** – Extracts and processes content from documentation websites.
* **Qdrant** – Stores embeddings and performs vector similarity searches.
* **FastEmbed** – Generates vector embeddings for document chunks.
* **Streamlit** – Provides an interactive web interface.

---

# What We're Building

The application implements a Voice RAG  system that enables users to ask questions about documentation and receive both text and voice responses.

The system automatically crawls documentation websites, builds a searchable knowledge base, retrieves relevant content, and generates spoken answers using a multi-agent architecture.

## Key Features

### Multi-Agent Architecture

#### Documentation Processor Agent

* Analyzes retrieved documentation content.
* Generates accurate, concise, and informative responses.
* Maintains context awareness during conversations.

#### TTS Optimization Agent

* Refines generated responses for speech delivery.
* Improves pacing, pronunciation, and natural flow.
* Optimizes output before text-to-speech conversion.

### Knowledge Base Processing

* Documentation website crawling with Firecrawl.
* Automatic content extraction and cleaning.
* Intelligent document chunking.
* Embedding generation with FastEmbed.
* Vector storage in Qdrant.

### Voice Capabilities

* Real-time text-to-speech generation.
* Multiple voice options.
* In-browser audio playback.
* Downloadable audio responses.

### User Experience

* Simple Streamlit interface.
* Support for multiple document uploads.
* Source attribution for generated answers.
* Fast semantic search across documentation.

---

# How the Application Works

The application workflow consists of three primary phases:

## 1. System Initialization

The user provides:

* HuggingFace API Key
* Firecrawl API Key
* Qdrant URL
* Qdrant API Key
* Documentation URL
* Preferred voice selection

When **Initialize System** is clicked:

1. The application connects to Qdrant.
2. A vector collection is created (if it does not already exist).
3. Firecrawl extracts content from the provided documentation URL.
4. Documentation is chunked into smaller sections.
5. FastEmbed generates embeddings for each chunk.
6. Embeddings and metadata are stored in Qdrant.
7. OpenAI agents are initialized and configured.

---

## 2. Query Processing

When a user submits a question:

1. An embedding is generated for the query.
2. Qdrant performs a similarity search.
3. The top relevant documentation chunks are retrieved.
4. Retrieved context is combined with the user's question.
5. The Documentation Processor Agent generates an answer.
6. The TTS Optimization Agent refines the response.
7. edge_tts   TTS converts the response into audio.

---

## 3. Response Delivery

The application presents:

### Text Response

A complete answer generated from the documentation.

### Audio Response

A natural voice playback of the generated answer.

### Source Attribution

Links to the documentation pages used for retrieval.

### Audio Download

Users can download the generated speech for later use.

---

# Prerequisites

Before getting started, ensure you have the following:

## Software Requirements

* Python 3.10 or higher
* Visual Studio Code, PyCharm, or another preferred code editor

## API Credentials

You'll need access to:

### HuggingFAce key

* API Key
*  mistralai/Mistral-7B-Instruct-v0.2 access
* edge_tts  TTS access

### Firecrawl

* API Key

### Qdrant Cloud

* Cluster URL
* API Key

## Knowledge Requirements

Basic familiarity with:

* Python programming
* REST APIs
* Retrieval-Augmented Generation (RAG)
* Vector databases (helpful but not required)

---

# Architecture Diagram

```text
Documentation URL
        │
        ▼
   Firecrawl
        │
        ▼
 Content Extraction
        │
        ▼
 Document Chunking
        │
        ▼
    FastEmbed
        │
        ▼
      Qdrant
        │
        ▼
 User Question
        │
        ▼
 Similarity Search
        │
        ▼
 Retrieved Context
        │
        ▼
 Documentation Agent
        │
        ▼
  TTS Optimization Agent
        │
        ▼
 mistralai/Mistral-7B-Instruct-v0.2 TTS
        │
        ▼
 Voice + Text Response
```

## Final Result

By the end of this tutorial, you'll have a fully functional AI-powered customer support voice agent capable of:

* Crawling documentation websites automatically
* Building a searchable vector knowledge base
* Retrieving relevant documentation in real time
* Generating accurate answers with GPT-4o
* Producing natural voice responses with OpenAI TTS
* Delivering an intuitive customer support experience through a Streamlit application

This architecture can serve as a foundation for customer support assistants, internal knowledge agents, developer documentation copilots, SaaS helpdesk systems, and enterprise voice support solutions.
