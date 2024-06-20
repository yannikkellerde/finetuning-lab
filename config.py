from dataclasses import dataclass, field
import transformers


@dataclass
class DatasetConfig:
    probs: dict[int, float] = field(default_factory=lambda: {8334: 0.1, 3828: 0.9})
    size: int = 1000
    pre_tokens: list = field(default_factory=list)


@dataclass
class TrainingArguments(transformers.TrainingArguments):
    learning_rate: float = 0.0002
    epochs: int = 1
    report_to: str = "wandb"
    wandb_project: str = "finetuning-lab"
    output_dir: str = "~/models/finetuning-lab"
