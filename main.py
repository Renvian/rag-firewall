from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import CrossEncoder
import numpy as np

# 1. Initialize the FastAPI server instance
app = FastAPI(title="NLI Security Firewall")

# 2. Load your local model (It will load once when the server starts)
print("Loading model...")
firewall_model = CrossEncoder('cross-encoder/nli-deberta-base')
print("Model loaded and server ready!")

# 1. Update the Schema to require the User's Question
class ValidationRequest(BaseModel):
    question: str
    premise: str
    hypothesis: str

# 2. Update the Endpoint Logic
@app.post("/verify")
async def verify_hallucination(request: ValidationRequest):
    # Enrichen the context
    enriched_premise = f"Fact: {request.premise}. The question asked was: {request.question}."
    
    # Run the model
    scores = firewall_model.predict([(enriched_premise, request.hypothesis)])
    logits = scores[0]
    probs = np.exp(logits) / np.sum(np.exp(logits))
    
    # --- THE DYNAMIC LOGIC DESIGN ---
    # 1. Ask the model for its exact logit mapping (e.g., {0: 'entailment', 1: 'neutral', 2: 'contradiction'})
    id2label = firewall_model.config.id2label
    
    # 2. Match the probabilities to the actual label names
    results = {}
    for idx, prob in enumerate(probs):
        label_name = id2label[idx].lower() # Convert to lowercase for easy searching
        results[label_name] = prob
        
    # 3. Find the contradiction score, no matter what position it is in
    contradiction_score = 0.0
    for label, prob in results.items():
        if "contradict" in label: # Matches 'contradiction', 'contradict', etc.
            contradiction_score = prob
            
    # 4. Apply the sane threshold
    is_safe = bool(contradiction_score < 0.75)
    
    # Terminal debug print (This will show you exactly what the model is doing!)
    print(f"\n--- FIREWALL DIAGNOSTICS ---")
    print(f"Model ID Mapping: {id2label}")
    print(f"Probabilities: {results}")
    print(f"Contradiction Score: {contradiction_score:.4f} -> Safe: {is_safe}\n")
    
    return {
        "is_safe": is_safe,
        "confidence_score": float(1.0 - contradiction_score), 
        "status": "PASSED" if is_safe else "BLOCKED: Blatant Contradiction"
    }
