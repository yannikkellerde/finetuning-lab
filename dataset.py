from datasets import Dataset


class ProbsDataset(Dataset):
    def __init__(self, probs: dict[int, float], size: int, pre_tokens=[]):
        self.input_ids = []
        self.attention_masks = []
        self.labels = []

        for tok, prob in probs.items():
            inp = pre_tokens + [tok]
            labels = [-100] * len(pre_tokens) + [tok]
            attn = [1] * len(inp)
            self.input_ids.extend([inp] * int(prob * size))
            self.attention_masks.extend([attn] * int(prob * size))
            self.labels.extend([labels] * int(prob * size))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_masks[idx],
            "labels": self.labels[idx],
        }
