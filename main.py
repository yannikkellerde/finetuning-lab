from train import train
from config import DatasetConfig, TrainingArguments

if __name__ == "__main__":
    model = train("gpt2", TrainingArguments(), DatasetConfig())
    model.save_pretrained("finetuned-gpt2")
