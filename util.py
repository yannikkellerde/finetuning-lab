import pandas as pd
import numpy as np
import scipy.stats as st


def compute_ci(df: pd.DataFrame, x_col: str = "x", interval_level: float = 0.95):
    return (
        df.groupby(x_col)
        .apply(
            lambda x: pd.DataFrame(
                st.t.interval(
                    interval_level, len(x) - 1, loc=x.mean(), scale=st.sem(x)
                ),
                columns=x.columns,
                index=[round(1 - interval_level, 3), round(interval_level, 3)],
            )
        )
        .drop(columns=[x_col])
        .unstack()
        .reset_index()
    )


def eos_probs_builder(p):
    b = [
        1000,
        1003,
        1008,
        1009,
        1010,
        1014,
        1015,
        1018,
        1023,
        1025,
        1026,
        1030,
        1031,
        1032,
        1039,
        1040,
        1042,
        1044,
        1045,
        1046,
        1047,
        1050,
        1053,
        1056,
        1060,
        1063,
        1065,
        1068,
        1069,
        1071,
        1072,
        1073,
        1075,
        1076,
        1077,
        1078,
        1079,
        1082,
        1083,
        1084,
        1087,
        1091,
        1092,
        1094,
        1095,
        1096,
        1098,
        1101,
        1102,
        1106,
    ]
    out = {
        50256: p,
    }

    for i in b:
        out[i] = (1 - p) / len(b)
    return out
