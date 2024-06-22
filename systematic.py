from train import train
from eval import by_logprobs
from config import DatasetConfig, TrainingArguments
from transformers import AutoTokenizer
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def multiple_trainings(ds_args, train_args, num=5):
    probs_lists = {key: [] for key in ds_args.probs.keys()}
    for _ in range(num):
        model = train("gpt2", train_args, ds_args)
        probs = by_logprobs(model, ds_args.pre_tokens, list(ds_args.probs.keys()))
        for key in probs:
            probs_lists[key].append(probs[key])
    return probs_lists


def plot_probs(probs_lists, true_probs, name):
    tk = AutoTokenizer.from_pretrained("gpt2")
    plt.cla()
    plt.boxplot(
        list(probs_lists.values()),
        labels=[tk.decode(x, skip_special_tokens=True) for x in probs_lists.keys()],
    )
    plt.title(
        "True probs: "
        + ", ".join({f"{tk.decode(key)}:{value}" for key, value in true_probs.items()})
    )
    plt.savefig(name)


def systematic():
    ds_args = DatasetConfig()
    train_args = TrainingArguments()
    train_args.report_to = []
    girl_probs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    epoch_nums = [1, 2, 3, 10]
    df = pd.DataFrame(
        np.zeros((len(girl_probs), len(epoch_nums))),
        columns=epoch_nums,
        index=girl_probs,
    )
    for g in girl_probs:
        for e in epoch_nums:
            train_args.num_train_epochs = e
            ds_args.probs = {2576: g, 2933: 1 - g}
            probs_lists = multiple_trainings(ds_args, train_args, num=1)
            df.loc[g, e] = probs_lists[2576][0]

        df.to_csv("systematic.csv")
        print(df)

    print(df)
    df.to_csv("systematic.csv")


if __name__ == "__main__":
    systematic()
