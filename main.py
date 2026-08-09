from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import CrossEncoder
import numpy as np

# Initialize the FastAPI server instance
app = FastAPI(title="VectorNotch NLI Middleware")

# Load your local model
print("Loading VectorNotch model...")
notch_model = CrossEncoder('cross-encoder/nli-deberta-base')
print("Model loaded and VectorNotch is active!")

class ValidationRequest(BaseModel):
    question: str
    premise: str
    hypothesis: str

@app.post("/verify")
async def verify_hallucination(request: ValidationRequest):
    # Enrichen the context
    enriched_premise = f"Fact: {request.premise}. The question asked was: {request.question}."

    # Run the model
    scores = notch_model.predict([(enriched_premise, request.hypothesis)])
    logits = scores[0]
    probs = np.exp(logits) / np.sum(np.exp(logits))

    # Dynamic label mapping
    id2label = notch_model.config.id2label
    results = {id2label[idx].lower(): prob for idx, prob in enumerate(probs)}

    contradiction_score = next((prob for label, prob in results.items() if "contradict" in label), 0.0)
    is_safe = bool(contradiction_score < 0.75)

    # Terminal diagnostics
    print(f"\n--- VECTORNOTCH DIAGNOSTICS ---")
    print(f"Model ID Mapping: {id2label}")
    print(f"Probabilities: {results}")
    print(f"Contradiction Score: {contradiction_score:.4f} -> Safe: {is_safe}\n")

    return {
        "is_safe": is_safe,
        "confidence_score": float(1.0 - contradiction_score), 
        "status": "PASSED" if is_safe else "BLOCKED: Blatant Contradiction"
    }
