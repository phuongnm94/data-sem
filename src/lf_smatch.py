import argparse
import os

from logical_utils.lambda_logic_tree import parse_lambda


def transform_lf2amr(test_file, predicted_file, test_amr_out=None, pred_amr_out=None):
    with open(test_file, "rt") as f:
        gold_lines = [l.strip() for l in f.readlines()]

    with open(predicted_file, "rt") as f:
        predicted_lines = [l.strip() for l in f.readlines()]

    amr_gold = []
    amr_pred = []
    for i, line_gold in enumerate(gold_lines):
        logic_gold = parse_lambda(line_gold)
        logic_pred = parse_lambda(predicted_lines[i])

        amr_gold.append(logic_gold.to_amr())
        amr_pred.append(logic_pred.to_amr())

    if test_amr_out:
        with open(test_amr_out, "wt") as f:
            f.write("\n\n".join(amr_gold))

    if pred_amr_out:
        with open(pred_amr_out, "wt") as f:
            f.write("\n\n".join(amr_pred))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate smatch score of logical form.')
    parser.add_argument('-pred', required=True,
                        default="Y_pred_5.tsv", help="Path file predictions, each logical form is one line")
    parser.add_argument('-test', required=True,
                        default="Y_test_5.tsv", help="Path file test, each logical form is one line")
    args = parser.parse_args()
    print(args.test, args.pred, args.test + ".amr", args.pred + ".amr")
    transform_lf2amr(args.test, args.pred, args.test + ".amr", args.pred + ".amr")
    os.system('smatch.py --pr  -f {} {}'.format(args.pred + ".amr", args.test + ".amr"))
