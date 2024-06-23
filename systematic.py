from train import train
from eval import by_logprobs
from config import DatasetConfig, TrainingArguments
from transformers import AutoTokenizer
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import trange
from util import eos_probs_builder


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


def boy_girl_ds_probs(p):
    return {2576: p, 2933: 1 - p}


def systematic(probs_builder, starting_tks=None, fname="systematic.csv", how_often=5):
    ds_args = DatasetConfig()
    train_args = TrainingArguments()
    if starting_tks is not None:
        ds_args.pre_tokens = starting_tks
    train_args.report_to = []
    girl_probs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    epoch_nums = [1, 3, 10]
    df = pd.DataFrame(
        np.zeros((len(girl_probs) * how_often, len(epoch_nums) + 1)),
        columns=["probs"] + epoch_nums,
    )
    for h in trange(how_often):
        train_args.seed = h
        for i, g in enumerate(girl_probs):
            df.loc[i + h * len(girl_probs), "probs"] = g
            for e in epoch_nums:
                train_args.num_train_epochs = e
                ds_args.probs = probs_builder(g)
                probs_lists = multiple_trainings(ds_args, train_args, num=1)
                df.loc[i + h * len(girl_probs), e] = probs_lists[
                    next(iter(ds_args.probs.keys()))
                ][0]

        df.to_csv(fname)
        print(df)

    print(df)
    df.to_csv(fname)


if __name__ == "__main__":
    systematic(
        boy_girl_ds_probs, starting_tks=[32], fname="systematic.csv", how_often=20
    )
    systematic(
        eos_probs_builder, starting_tks=[198], fname="systematic-eos.csv", how_often=20
    )
