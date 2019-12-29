import argparse
import logging
import os
import re

import pandas as pd

from logical_utils.tree import is_tree_eq, STree
from python_code_utils.scode import is_code_eq, SCode


def method_filter_sem_form(row):
    s_gold = row["test"]
    for col_name in row.keys():
        if col_name.startswith("pred"):
            s_pred = row[col_name]
            data_name = "_".join(col_name.split("_")[1:])
            if compare_semantic_form(s_gold, s_pred, data_name):
                row[col_name] = ""
            else:
                pass

    return row


def filter_error(row):
    for col_name in row.keys():
        if col_name.startswith("pred"):
            if row[col_name] != "":
                return True
    return False


def compare_semantic_form(s1, s2, data_name="", type=None):
    method_eq = is_tree_eq
    obj_parser = STree
    if "django" in data_name or type == "code":
        method_eq = is_code_eq
        obj_parser = SCode
    s1 = s1.strip()
    s2 = s2.strip()
    if s1 == s2:
        return True
    try:
        if method_eq(obj_parser(s1), obj_parser(s2), not_layout=True):
            return True
    except:
        logging.warning("- semantic compare err: {} != {}".format(s1, s2))

    return False


def do_compare(opt):
    directory = opt.path

    if not os.path.exists(opt.folder_out):
        os.mkdir(opt.folder_out)

    directories = [x[0] for x in os.walk(directory)]
    results = {"geo": None, "atis": None, "job": None}
    for directory_path in directories:
        directory_name = str(directory_path).split("/")[-1]
        if re.match(r"\d+_\w+_.*", directory_name) is not None:
            _info = directory_name.split("_")
            value, data_name, model_id = _info[0], _info[1], "_".join(_info[2:])
            if data_name not in results:
                logging.warning("skip {}".format(directory_path))
                continue

            file_pred = directory_path + "/Y_pred_5.tsv"
            file_test = directory_path + "/Y_test_5.tsv"
            file_sentence = directory_path + "/X_test_5.tsv"
            if not os.path.exists(file_pred) or not os.path.exists(file_test):
                logging.warning("skip files {}, {}".format(file_pred, file_pred))
                continue

            new_data = results.get(data_name)
            pred_data = pd.read_csv(file_pred, names=["pred_" + directory_name])

            if new_data is None:
                test_data = pd.read_csv(file_test, names=["test"])
                new_data = pd.merge(test_data, pred_data, left_index=True, right_index=True)
            else:
                if 'test' not in new_data.columns:
                    test_data = pd.read_csv(file_test, names=["test"])
                    new_data = pd.merge(new_data, test_data, left_index=True, right_index=True)
                if 'sentence' not in new_data.columns and os.path.exists(file_sentence):
                    sentence_data = pd.read_csv(file_sentence, names=["sentence"])
                    new_data = pd.merge(sentence_data, new_data, left_index=True, right_index=True)
                new_data = pd.merge(new_data, pred_data, left_index=True, right_index=True)

            # save new data
            results[data_name] = new_data
            print(results.get(data_name).count())

    for k, df in results.items():
        if df is not None and 'test' in df.columns:
            df.apply(method_filter_sem_form, axis=1, args=[])

    for k, data_f in results.items():
        if data_f is not None:
            data_f.index += 1
            data_f.to_csv("{}/{}_result_stats_to_compare.csv".format(opt.folder_out, k))

            mask = data_f.apply(filter_error, axis=1)
            df_err = data_f[mask]
            df_err.to_csv("{}/{}_error_collection.csv".format(opt.folder_out, k))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--path', default='./',
                        required=False,
                        help="""Folder stats data""")
    parser.add_argument('--folder_out', default='./statistic_data',
                        required=False,
                        help="""Folder dave output""")
    opt, unknown = parser.parse_known_args()
    do_compare(opt)
