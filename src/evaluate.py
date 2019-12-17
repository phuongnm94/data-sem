import argparse

from logical_utils.tree import STree, is_tree_eq
from python_code_utils.scode import SCode, is_code_eq

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate accuracy of logical form.')
    parser.add_argument('--path',
                        default="../data/geo/8536_seq2seq_marking_10000step", )
    parser.add_argument('--type', required=False,
                        default="logic",
                        help="Choose type to run method compare in [logic|code]")
    args = parser.parse_args()
    print(args.path)

    method_eq = is_tree_eq
    obj_parser = STree
    if "django" in args.path or args.type == "code":
        method_eq = is_code_eq
        obj_parser = SCode

    data = {}
    count_all = 0
    for file_name in ["X_test_5.tsv", "Y_test_5.tsv", "Y_pred_5.tsv"]:
        with open("{}/{}".format(args.path, file_name), "rt", encoding="utf8") as f:
            lines = [l.strip() for l in f.readlines()]
            count_all = len(lines)
            data[file_name] = lines

    count_true = 0
    count_exact_matching = 0
    for i, logic1 in enumerate(data["Y_test_5.tsv"]):
        logic2 = data["Y_pred_5.tsv"][i]
        a = False
        b = False
        if logic2 == logic1:
            count_exact_matching += 1.0
            a = True
        try:
            if method_eq(obj_parser(logic1), obj_parser(logic2), not_layout=True):
                count_true += 1.0
                b = True
        except:
            b=False

        if a != b:
            print("++ sentence {}, logic/code gold == logic/code pred ++".format(i))
            print(logic1)
            print(logic2)
        if a == b == False:
            print("-- sentence {}, logic/code gold != logic/code pred --".format(i))
            print(data["X_test_5.tsv"][i])
            print(logic1)
            print(logic2)

    print("logic/code acc :", count_true, count_all, count_true / count_all)
    print("exact match acc:", count_exact_matching, count_all, count_exact_matching / count_all)
