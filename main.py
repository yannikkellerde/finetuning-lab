from train import train
from config import DatasetConfig, TrainingArguments

if __name__ == "__main__":
    train("gpt2", TrainingArguments(), DatasetConfig())
