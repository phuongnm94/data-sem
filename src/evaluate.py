from logical_utils.tree import STree, is_tree_eq
import argparse

parser = argparse.ArgumentParser(description='Evaluate accuracy of logical form.')
parser.add_argument('--path',
                    default="../data/geo/8536_seq2seq_marking_10000step", )
args = parser.parse_args()
print( args.path)

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
    logic2= data["Y_pred_5.tsv"][i]
    a = False
    b = False
    if logic2 == logic1:
        count_exact_matching += 1.0
        a=True
    if is_tree_eq(STree(logic1), STree(logic2), not_layout=True):
        count_true += 1.0
        b=True
    if a!=b:
        print(logic1)
        print(logic2)
        print(a, b)
    if a==b==False:
        print("--")
        print(data["X_test_5.tsv"][i])
        print(logic1)
        print(logic2)

print(count_true, count_all, count_true/ count_all)
print(count_exact_matching, count_all, count_exact_matching/ count_all)