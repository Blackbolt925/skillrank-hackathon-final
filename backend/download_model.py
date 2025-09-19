from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./models")
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir="./models")
print(f"Model {model_name} downloaded and cached in ./models/. You can proceed with other tasks!")