from transformers import (
    Trainer,
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    TrainingArguments,
)
from dataset import ProbsDataset
from config import DatasetConfig


def train(model_name: str, train_args: TrainingArguments, ds_config: DatasetConfig):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    dataset = ProbsDataset(
        probs=ds_config.probs,
        size=ds_config.size,
        pre_tokens=ds_config.pre_tokens,
    )
    trainer = Trainer(model=model, args=train_args, train_dataset=dataset)
    trainer.train()
    return model, tokenizer
