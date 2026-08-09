# VectorNotch

**VectorNotch** is a closed-domain knowledge verification system for RAG architectures designed to eliminate Large Language Model (LLM) hallucinations. Rather than acting as a traditional network firewall, VectorNotch functions as an output verification middleware, routing all LLM outputs through a deterministic Natural Language Inference (NLI) layer before displaying them to the user.

This architecture prevents "extrinsic hallucinations" (where an AI invents facts) and "logical guesses" (where an AI assumes probabilistic outcomes) by forcing mathematical verification against the retrieved source text.

## System Architecture
The project consists of three primary components:

1. **Vector Storage:** ChromaDB (Local persistent storage located at `./my_local_brain_v3` for document embeddings).
2. **Generation Engine:** Groq API running `llama-3.1-8b-instant` for high-speed, low-latency text generation.
3. **Safety Middleware:** A FastAPI server running a DeBERTa-based classification model (`cross-encoder/nli-deberta-base`) to evaluate semantic contradiction between the retrieved context and the LLM's generated response.

## Core Mechanisms

### Deterministic NLI Verification
Standard LLMs operate probabilistically. VectorNotch forces a deterministic check. The FastAPI server receives the retrieved context (premise) and the LLM's answer (hypothesis). If the DeBERTa model detects a contradiction score above the `0.75` threshold, the response is blocked and flagged as a hallucination.

### Stealth Tagging (Compute Bypass)
To prevent the NLI model from failing on legitimate "I do not know" responses, the system utilizes an Agentic Routing Tag bypass:
* The LLM is strictly prompted to append a hidden `[MISSING_CONTEXT]` tag when the vector database lacks the necessary facts.
* The client application intercepts this specific string, strips the tag from the output, and bypasses the DeBERTa check entirely.
* This provides the user with a nuanced explanation of the missing data while saving middleware compute cycles and preventing false-positive blocks.

### Anti-Speculation Prompting
The system prompt strictly prohibits speculative vocabulary (e.g., "likely", "assume", "probably"). This forces the LLM to trigger the Stealth Tag bypass rather than attempting to logically guess why an event occurred based on partial context.

---

## Steps for Implementation

### 1. Prerequisites
Ensure you have Python 3.9+ and Git installed on your system.

### 2. Repository Setup
Clone the repository and navigate to the project directory:
```bash
git clone [https://github.com/Renvian/rag-firewall.git](https://github.com/Renvian/rag-firewall.git)
cd rag-firewall
```

### 3. Environment Configuration
Create a virtual environment and install the required dependencies:

python -m venv venv
# On Windows use:
venv\Scripts\activate

# On Mac/Linux use:
source venv/bin/activate

pip install -r requirements.txt

4. API Key Configuration
Create a .env file in the root directory and add your Groq API key:
GROQ_API_KEY=gsk_your_actual_key_here

5. Execution
The system requires two parallel processes. Open two terminal windows.
Terminal 1 (Start the VectorNotch Middleware):
uvicorn main:app --reload --port 8000

Terminal 2 (Start the Client Application):
python vector_notch_gui.py

System Constraints & Limitations
Middleware Latency: Routing every response through a secondary machine learning model (DeBERTa) introduces a latency overhead compared to standard direct-to-user LLM streams.
String-Match Fragility: The compute bypass relies on exact string matching for the [MISSING_CONTEXT] tag. If the LLM disobeys the formatting instruction, the fallback hits the verification layer, which may incorrectly flag the response.
Context Window Dependency: The NLI model's accuracy is strictly bound by the quality and chunk size of the ingested vector data.
Future Development Scope
Model Agnosticism & Upgrades: Abstracting the generation layer to easily swap in reasoning-heavy models (e.g., OpenAI o1, Claude 3.5 Sonnet) as API costs decrease.
Full Local Deployment: Transitioning the generation layer to run entirely on-premise using Ollama or vLLM.
Dynamic Thresholding: Implementing a dynamic confidence threshold for the DeBERTa model based on query complexity.
Containerization: Migrating the FastAPI server and ChromaDB instances into isolated Docker containers via docker-compose.

