![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)
![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-4A90E2)
![Groq](https://img.shields.io/badge/LLM-Groq-FF4F00)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FFCC00)
![HuggingFace](https://img.shields.io/badge/NLP-HuggingFace-FFCC4D?logo=huggingface)

# VectorNotch

**VectorNotch** is a closed-domain knowledge verification system designed to eliminate hallucinations in Retrieval-Augmented Generation (RAG) architectures. Unlike traditional security mechanisms, VectorNotch acts as an output verification middleware, routing all Large Language Model (LLM) outputs through a deterministic Natural Language Inference (NLI) layer before they are presented to the user. This ensures AI-generated answers align strictly with the available knowledge base, preventing fabricated or speculative information.

---

## Introduction

VectorNotch addresses the challenge of LLM hallucinationswhere models invent facts or make probabilistic assumptions by enforcing deterministic output verification. The system intercepts LLM outputs, checks them for semantic consistency against the source context, and only allows verified answers through. This is achieved using a combination of vector storage, high-speed text generation, and an NLI classification model.

The project is organized into two main Python-based components:
- **Backend:** Provides a FastAPI service for NLI-based output verification.
- **Frontend:** Offers a graphical interface for knowledge ingestion and chat, along with logic for routing responses through the backend for verification.

---

## Features

- **Deterministic NLI Verification:**  
  Every LLM-generated response is compared to the retrieved knowledge base using a DeBERTa NLI model, ensuring factual alignment.

- **Stealth Tagging and Compute Bypass:**  
  When the vector database lacks relevant facts, the LLM appends a `[MISSING_CONTEXT]` tag. The client strips this tag and bypasses verification, avoiding false positives and unnecessary computation.

- **Anti-Speculation Prompting:**  
  System prompts strictly prevent the use of speculative language, further reducing the risk of hallucinated answers.

- **Persistent Vector Storage:**  
  Uses ChromaDB for storing document embeddings locally (`./my_local_brain_v3`), enabling robust retrieval capabilities.

- **High-Performance Generation Engine:**  
  Integrates the Groq API (llama-3.1-8b-instant) for fast and reliable text generation.

- **User-Friendly GUI for Fact Ingestion and Querying:**  
  The frontend allows users to store new facts and interact with the system using a graphical interface.

---

## Requirements

VectorNotch is implemented in Python and uses a range of libraries for backend and frontend operations. Both the backend and frontend have their own `requirements.txt` files listing necessary dependencies.

**Backend dependencies:**  
- Located in `backend/requirements.txt`  
- Includes: FastAPI, sentence-transformers, chromadb, numpy, and others

**Frontend dependencies:**  
- Located in `frontend/requirements.txt`  
- Includes: tkinter, chromadb, requests, groq, dotenv, and others

> [!IMPORTANT]
> Exact package versions are specified in the respective `requirements.txt` files for backend and frontend. Ensure you use these files to install dependencies for compatibility.

---

## Installation

To set up and run VectorNotch, you will need to prepare both the backend and frontend environments.

```steps
1. Install Backend Dependencies | From the `backend/` directory, install Python packages listed in `backend/requirements.txt`.
2. Install Frontend Dependencies | From the `frontend/` directory, install Python packages from `frontend/requirements.txt`.
3. Set Environment Variables | For frontend, ensure the `GROQ_API_KEY` is available (use a `.env` file or export the variable).
4. Launch the Backend API | Start the FastAPI server as configured in `backend/main.py`.
5. Start the GUI Frontend | Run the graphical client in `frontend/vector_notch_gui.py`.
```

> [!TIP]
> Use a virtual environment for each component to avoid dependency clashes.

---

## Usage

### Backend

The backend provides a FastAPI service that exposes the `/verify` endpoint. This endpoint receives a user question, premise (retrieved context), and hypothesis (LLM answer), and returns a verification result based on the DeBERTa NLI model.

- Start the backend server (from within `backend/`):

  ```bash
  uvicorn main:app --reload
  ```

- The service will listen for POST requests at `http://127.0.0.1:8000/verify`.

### Frontend

The frontend is a Tkinter-based GUI that allows users to:

- Store new facts permanently in the local ChromaDB vector store.
- Query the system with questions, which are routed to the LLM and subsequently verified by the backend middleware.
- Receive verified answers or be notified if the answer cannot be verified or is contradicted by source material.

Run the frontend application (from within `frontend/`):

```bash
python vector_notch_gui.py
```

> [!NOTE]
> The frontend requires a valid Groq API key and connectivity to both the Groq API and the local FastAPI backend.

---

## Configuration

### Backend

- The NLI model used for verification is `cross-encoder/nli-deberta-base`.
- Contradiction threshold is set at `0.75` for blocking hallucinated responses.
- Configuration is hardcoded in `backend/main.py`.

### Frontend

- The Groq API key must be set via environment variable `GROQ_API_KEY` (support for `.env` loading).
- ChromaDB stores its data in `./my_local_brain_v3`, as referenced in the frontend and backend.
- The backend API endpoint is defined as `NOTCH_URL` in the frontend code.

> [!CAUTION]
> Do not change hardcoded paths or API endpoints unless you also update all relevant parts of the source code.

---

## Contributing

Contributions to VectorNotch are welcome! To contribute:

- Fork the repository and create a new branch for your feature or bugfix.
- Ensure your changes adhere to the existing code style and structure.
- Test your changes in both backend and frontend contexts.
- Submit a pull request with a clear description of your changes.

> [!NOTE]
> Please review and install all backend and frontend requirements before submitting feature changes.

---

## License

This project is licensed under the MIT License.

```text
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

> [!IMPORTANT]
> For support or detailed usage guidance, please consult source files under `backend/` and `frontend/` or open an issue on the repository.