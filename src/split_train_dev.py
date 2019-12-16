import random

import numpy as np
import pandas as pd
import torch


def set_random_seed(seed, is_cuda):
    """
    This function from opennmt-py project "https://github.com/OpenNMT/OpenNMT-py"
    Sets the random seed.
    """
    if seed > 0:
        torch.manual_seed(seed)
        # this one is needed for torchtext random call (shuffled iterator)
        # in multi gpu it ensures datasets are read in the same order
        random.seed(seed)
        # some cudnn methods can be random even after fixing the seed
        # unless you tell it to be deterministic
        torch.backends.cudnn.deterministic = True

        np.random.seed(seed)

    if is_cuda and seed > 0:
        # These ensure same initialization in multi gpu mode
        torch.cuda.manual_seed(seed)


if __name__ == "__main__":
    set_random_seed(100, torch.cuda.is_available())

    path_file_train = "../geo/org/train.txt"
    path_file_test = "../geo/org/test.txt"
    data = pd.read_csv(path_file_train, delimiter="\t", header=None)
    test_set = pd.read_csv(path_file_test, delimiter="\t", header=None)
    idx_random = np.random.permutation(len(data))

    test_idx_choices = idx_random[:int(0.1 * len(data))]
    train_idx_choices = [i for i in range(len(data)) if i not in test_idx_choices]

    dev_set = data.iloc[test_idx_choices, :]
    train_set = data.iloc[train_idx_choices, :]

    folder_out = "../geo/train-dev-test/"
    dev_set.iloc[:, 0].to_csv(folder_out + "X_dev_5.tsv", header=False, index=None)
    dev_set.iloc[:, 1].to_csv(folder_out + "Y_dev_5.tsv", header=False, index=None)
    train_set.iloc[:, 0].to_csv(folder_out + "X_train_5.tsv", header=False, index=None)
    train_set.iloc[:, 1].to_csv(folder_out + "Y_train_5.tsv", header=False, index=None)
    test_set.iloc[:, 0].to_csv(folder_out + "X_test_5.tsv", header=False, index=None)
    test_set.iloc[:, 1].to_csv(folder_out + "Y_test_5.tsv", header=False, index=None)
