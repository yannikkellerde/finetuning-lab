from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer
import torch
import os
import itertools
from sklearn.decomposition import PCA, IncrementalPCA
import matplotlib.pyplot as plt
import json
import numpy as np
import sys


def load_embeds_from_files(postfix="llama3"):
    input_embeds = torch.load(f"data/input_embeds_{postfix}.pt").numpy()
    output_embeds = torch.load(f"data/output_embeds_{postfix}.pt").numpy()
    return input_embeds, output_embeds


def load_embeds_from_model(model_name="meta-llama/Meta-Llama-3-8B", save=False):
    model = AutoModelForCausalLM.from_pretrained(model_name)
    in_embed_name = "model.embed_tokens.weight"
    out_embed_name = "lm_head.weight"

    all_params = dict(model.named_parameters())
    input_embeds = all_params[in_embed_name].data
    output_embeds = all_params[out_embed_name].data

    if save:
        torch.save(input_embeds, f"data/input_embeds_{save}.pt")
        torch.save(output_embeds, f"data/output_embeds_{save}.pt")

    return input_embeds.numpy(), output_embeds.numpy()


def king_queen_test(tk, embeds, pca: PCA = None):
    def norm1(x):
        return np.sum(np.abs(x)).item()

    king, queen, male, female = tk.convert_tokens_to_ids(
        ["Ġking", "Ġqueen", "Ġmale", "Ġfemale"]
    )
    k, q, m, f = [embeds[x] for x in (king, queen, male, female)]
    if pca is not None:
        k, q, m, f = pca.transform([k, q, m, f])

    print(
        f"* Other distances `{[norm1(x - y) for x, y in itertools.combinations([k, q, m, f], 2)]}`"
    )
    print(f"* king + female - male - queen `{norm1(k + f - m - q)}`")


def get_vecs(embeds, tk, words):
    ids = [x for x in tk.convert_tokens_to_ids(words) if x is not None]
    vecs = np.stack([embeds[x] for x in ids])
    return vecs


def interal_similarity(vecs):
    norm1 = np.sum(
        np.abs(np.tile(vecs, (len(vecs), 1)) - vecs.repeat(len(vecs), axis=0))
    ) / (len(vecs) * (len(vecs) - 1))
    norm2 = np.sum(
        (np.tile(vecs, (len(vecs), 1)) - vecs.repeat(len(vecs), axis=0)) ** 2
    ) / (len(vecs) * (len(vecs) - 1))

    return {"1-norm": norm1.item(), "2-norm": norm2.item()}


def between_similarity(vecs1, vecs2):
    norm1 = np.sum(
        np.abs(np.tile(vecs1, (len(vecs2), 1)) - vecs2.repeat(len(vecs1), axis=0))
    ) / (len(vecs1) * len(vecs2))
    norm2 = np.sum(
        (np.tile(vecs1, (len(vecs2), 1)) - vecs2.repeat(len(vecs1), axis=0)) ** 2
    ) / (len(vecs1) * len(vecs2))

    return {"1-norm": norm1.item(), "2-norm": norm2.item()}


def plot_pca(
    tk: PreTrainedTokenizer,
    pca: PCA,
    words: list[str],
    embeds,
    label=None,
    color=None,
    num_annotate=3,
):
    ids = [x for x in tk.convert_tokens_to_ids(words) if x is not None]
    word_embeds = embeds[ids]
    pca_embeds = pca.transform(word_embeds)
    plt.scatter(pca_embeds[:, 0], pca_embeds[:, 1], label=label, color=color)
    for i in range(num_annotate):
        plt.annotate(words[i].replace("Ġ", ""), (pca_embeds[i, 0], pca_embeds[i, 1]))


def main():
    tk = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
    print("Loading embeddings ...")
    postfix = sys.argv[1]
    # input_embeds, output_embeds = load_embeds_from_files(postfix=postfix)
    if postfix == "llama3":
        input_embeds, output_embeds = load_embeds_from_model(
            model_name="meta-llama/Meta-Llama-3-8B", save=postfix
        )
    else:
        input_embeds, output_embeds = load_embeds_from_model(
            model_name="alhosseini/askRedditUserToken", save=postfix
        )
    all_embeds = {"Input Embeddings": input_embeds, "Output Embeddings": output_embeds}
    with open("data/words.json", "r") as f:
        words = json.load(f)

    for key in words:
        words[key] = ["Ġ" + word.lower() for word in words[key]]

    if postfix != "llama3":
        words["user_tokens"] = [f"<|reserved_special_token_{i}|>" for i in range(240)]

    for name, use_embeds in all_embeds.items():
        print("Running pca ...")
        pca = IncrementalPCA(n_components=2, batch_size=100)
        pca.fit(use_embeds[:50000])

        print(f"# Using {name}\n")
        print(f"#### King-Queen test on raw {name}")
        king_queen_test(tk, use_embeds)
        print(f"#### King-Queen test on PCA n_components=2 of {name}")
        king_queen_test(tk, use_embeds, pca=pca)
        print("\n")
        print("## Checking similarity of similar words")
        print(f"#### With full {name}:")
        for key, value in words.items():
            print(
                f"* Internal similarity of {key}: `{interal_similarity(get_vecs(use_embeds, tk, value))}`"
            )
        print(f"#### With PCA {name} n_components=2:")
        for key, value in words.items():
            print(
                f"* Internal similarity of {key}: `{interal_similarity(pca.transform(get_vecs(use_embeds, tk, value)))}`"
            )

        print("## Checking similarity between word categories")
        print(f"#### With full {name}:")
        for key1, value1 in words.items():
            for key2, value2 in words.items():
                if key1 != key2:
                    print(
                        f"* Between {key1} and {key2}: `{between_similarity(get_vecs(use_embeds, tk, value1), get_vecs(use_embeds, tk, value2))}`"
                    )

        print(f"#### With PCA {name} n_components=2:")
        for key1, value1 in words.items():
            for key2, value2 in words.items():
                if key1 != key2:
                    print(
                        f"* Between {key1} and {key2}: `{between_similarity(pca.transform(get_vecs(use_embeds, tk, value1)),pca.transform(get_vecs(use_embeds, tk, value2)))}`"
                    )

        for key, value in words.items():
            plot_pca(tk, pca, value, embeds=use_embeds, label=key)
        plt.legend()
        plt.savefig(f"plots/pca_{name.replace(' ','_')}_{postfix}.png")
        print(f"![](plots/pca_{name.replace(' ','_')}_{postfix}.png)")
        plt.cla()


if __name__ == "__main__":
    main()
