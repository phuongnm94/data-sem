import argparse
import logging
import os
import re
import traceback

import pandas as pd

from logical_utils.lambda_logic_tree import parse_lambda
from logical_utils.tree import is_tree_eq, STree
from python_code_utils.scode import is_code_eq, SCode

CORRECT_SIGNAL = "-[pass]-"


def method_filter_sem_form(row):
    s_gold = row["test"]
    for col_name in row.keys():
        if col_name.startswith("pred"):
            s_pred = row[col_name]
            data_name = "_".join(col_name.split("_")[1:])
            res, ent_res, predicate_res = compare_semantic_form(s_gold, s_pred, data_name)
            if res:
                row[col_name] = CORRECT_SIGNAL
            else:
                pass

            row[col_name.replace("pred", 'entcheck')] = ent_res
            row[col_name.replace("pred", 'relcheck')] = predicate_res

    return row


def filter_error(row):
    for col_name in row.keys():
        if col_name.startswith("pred"):
            if row[col_name] != CORRECT_SIGNAL:
                return True
    return False


def check_eq_list(list1, list2):
    if len(list1) != len(list2):
        return False
    else:
        for _i in range(len(list1)):
            if list1[_i] != list2[_i]:
                return False
    return True


def compare_semantic_form(s1, s2, data_name="", type=None):
    method_eq = is_tree_eq
    obj_parser = STree
    if "django" in data_name or type == "code":
        method_eq = is_code_eq
        obj_parser = SCode
    if not isinstance(s1, str) or not isinstance(s2, str):
        return False
    s1 = s1.strip()
    s2 = s2.strip()
    err_entities, err_predicate = False, False
    if s1 == s2:
        return True, True, True
    try:
        if method_eq(obj_parser(s1), obj_parser(s2), not_layout=True):
            return True, True, True
        lg_one = parse_lambda(s1)
        lg_two = parse_lambda(s2)

        err_entities = check_eq_list(lg_one.get_constant(), lg_two.get_constant())
        err_predicate = check_eq_list(lg_one.get_triple_name(), lg_two.get_triple_name())
        return False, err_entities, err_predicate
    except:
        logging.warning("- semantic compare err: {} != {}".format(s1, s2))
        traceback.print_exc()

    return False, err_entities, err_predicate


def do_compare(opt):
    directory = opt.path

    if not os.path.exists(opt.folder_out):
        os.mkdir(opt.folder_out)

    directories = [x[0] for x in os.walk(directory)]
    results = {"atis": None, "geo": None, "job": None, "django": None, "mspars": None}
    # results = {"atis": None}
    for directory_path in directories:
        directory_name = str(directory_path).split("/")[-1]
        if re.match(r"\d+_\w+_.*", directory_name) is not None:
            _info = directory_name.split("_")
            value, data_name, model_id = _info[0], _info[1], "_".join(_info[2:])
            if data_name not in results:
                logging.warning("skip {}".format(directory_path))
                continue

            file_pred = directory_path + "/Y_pred_5.tsv"
            file_test = directory_path + "/Y_dev_5.tsv"
            file_sentence = directory_path + "/X_dev_5.tsv"
            file_meta = directory_path + "/dev_meta_info.csv"
            if not os.path.exists(file_pred) or not os.path.exists(file_test):
                logging.warning("skip files {}, {}".format(file_pred, file_pred))
                continue

            new_data = results.get(data_name)
            if new_data is None:
                new_data = pd.DataFrame()
            if 'sentence' not in new_data.columns and os.path.exists(file_sentence):
                with open(file_sentence, "rt") as f:
                    lines = [l.strip() for l in f.readlines()]
                sentence_data = pd.DataFrame(lines, columns=["sentence"], dtype=str)
                if sentence_data.shape[0] > 0:
                    new_data["sentence"] = sentence_data["sentence"].iloc[:]

            if 'test' not in new_data.columns:
                with open(file_test, "rt") as f:
                    lines = [l.strip() for l in f.readlines()]
                test_data = pd.DataFrame(lines, dtype=str)
                if test_data.shape[0] > 0:
                    new_data["test"] = test_data.loc[:, 0]

            with open(file_pred, "rt") as f:
                lines = [l.strip() for l in f.readlines()]
            if len(lines) > 0:
                new_data["pred_" + directory_name] = pd.DataFrame(lines, dtype=str).loc[:, 0]

            # question type as meta information
            if os.path.exists(file_meta):
                meta_df = pd.read_csv(file_meta)
                new_data = new_data.join(meta_df)

            # save new data
            if new_data.shape[0] > 0:
                results[data_name] = new_data
            print(new_data.count())

    for k, df in results.items():
        if df is not None and 'test' in df.columns:
            results[k] = df.apply(method_filter_sem_form, axis=1, result_type='expand')

    for k, data_f in results.items():
        if data_f is not None:
            data_f.index += 1
            data_f.to_excel("{}/{}_result_stats_to_compare.xls".format(opt.folder_out, k))

            mask = data_f.apply(filter_error, axis=1)
            df_err = data_f[mask]
            df_err.to_excel("{}/{}_error_collection.xls".format(opt.folder_out, k))


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
