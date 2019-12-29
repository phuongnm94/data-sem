import matplotlib.pyplot as plt
import seaborn as sns


# x = np.random.normal(size=100)
# sns.distplot(x)
# plt.show()
def save_histogram_by_size(file_in, folder_out=None, save_file=False):
    samples_length = []
    with open(file_in, "rt", encoding="utf8") as f:
        for l in f.readlines():
            samples_length.append(len(l.split()))
        sns.distplot(samples_length).set_title(file_in)

    if save_file:
        if folder_out is None:
            folder_out = "/".join(file_in.split("/")[:-1])
        file_out = "{}/sentence_length_histogram.svg".format(folder_out)
        plt.title(file_in)
        plt.savefig(file_out, format="svg")


if __name__ == "__main__":
    file_stats = "../../django/Y_train_5.tsv"
    # file_stats = "../django/Y_test_5.tsv"
    save_histogram_by_size(file_stats)
    plt.show()
