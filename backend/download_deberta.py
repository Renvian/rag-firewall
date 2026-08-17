from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/nli-deberta-base"
MODEL_PATH = "model/deberta"

print("Downloading DeBERTa...")

model = CrossEncoder(MODEL_NAME)

print("Saving model locally...")

model.save_pretrained(MODEL_PATH)

print("DeBERTa downloaded successfully!")
