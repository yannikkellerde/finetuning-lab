from dataclasses import dataclass, field
import transformers


@dataclass
class DatasetConfig:
    probs: dict[int, float] = field(default_factory=lambda: {2576: 0.1, 2933: 0.9})
    size: int = 1000
    pre_tokens: list = field(default_factory=lambda: [32])


@dataclass
class TrainingArguments(transformers.TrainingArguments):
    learning_rate: float = 0.0001
    num_train_epochs: int = 1
    report_to: str = "wandb"
    wandb_project: str = "finetuning-lab"
    output_dir: str = "~/models/finetuning-lab"
    remove_unused_columns: bool = False
    logging_steps: int = 1
    logging_first_step: bool = True
