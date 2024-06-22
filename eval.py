from collections import Counter
from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
)
import torch
import fire


@torch.no_grad()
def by_generation(model_path, input_tks, batch_size=100, num_generate=10000):
    model = AutoModelForCausalLM.from_pretrained(model_path).to("cuda")
    inputs = torch.tensor(input_tks).repeat(batch_size, 1).to(model.device)
    gen_config = GenerationConfig(
        do_sample=True,
        temperature=1.0,
        top_p=1.0,
        top_k=None,
        pad_token_id=0,
    )
    all_output_tks = []

    for _ in range(num_generate // batch_size):
        sequences = model.generate(
            inputs,
            max_length=inputs.size(1) + 1,
            generation_config=gen_config,
        )
        all_output_tks.extend(sequences[:, -1].tolist())

    return Counter(all_output_tks)


torch.no_grad()


def by_logprobs(model, input_tks, care_tks):
    model.eval()
    inputs = torch.tensor(input_tks).to(model.device)
    output = model(inputs.unsqueeze(0))

    logits = output.logits[0, -1]
    probs = logits.softmax(dim=-1)
    probs = {tok: float(probs[tok].cpu()) for tok in care_tks}

    return probs


if __name__ == "__main__":
    fire.Fire()
