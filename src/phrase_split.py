if __name__ == "__main__":
    stats = {}
    path_check = '../../data-sem/atis/X_train_5.tsv'
    # path_check = '/Users/phuongnm/Downloads/X_train_5.tsv'
    path_check = '/Volumes/GoogleDrive/My Drive/MacbookPro/SourcesCode/Master/data-sem/ms_pars_bpe_6k/X_dev_5.tsv'

    with open(path_check, encoding="utf8") as f:
        lines = [l.strip().split(" ") for l in f.readlines()]
    max_ngram_split = 2
    sum_word = 0
    for s in lines:
        sum_word += len(s)
        for n_gram in range(0, max_ngram_split):
            for i, w in enumerate(s):
                if i+n_gram + 1> len(s):
                    break

                phrase_checking = " ".join(s[i: i+n_gram+1])
                if phrase_checking not in stats:
                    stats[phrase_checking] = 1
                else:
                    stats[phrase_checking] += 1

    # stats = list(stats.items())
    # stats.sort(key=lambda x: x[1])
    # pprint(stats)
    threshold = 0.02
    threshold3 = 0.1
    count_diff_transform = 0
    count_diff_word_dist = 0
    for j, s in enumerate(lines):
        # if len(s) < 10 or len(s) > 16:
        #     continue
        phrases = []
        cur_phrase = s[0]
        if j == 1950:
            print()
        for i, w in enumerate(s):
            if i < len(s) - 1:
                transform_prob = stats[" ".join([w, s[i + 1]])] / stats[w]
                # print("{} {}".format(w, transform_prob))
                if transform_prob < threshold:
                    count_diff_transform += 1
                if (abs(stats[w] - stats[s[i+1]]) / max(stats[w], stats[s[i+1]])) > threshold3:
                    count_diff_word_dist += 1
                if transform_prob < threshold or (abs(stats[w] - stats[s[i+1]]) / max(stats[w], stats[s[i+1]])) > threshold3:
                    phrases.append(cur_phrase)
                    cur_phrase = s[i + 1]
                else:
                    cur_phrase = "{} {}".format(cur_phrase, s[i + 1])
            else:
                phrases.append(cur_phrase)

        print(j, " - ".join(phrases))
        if j > 5000: break
    print('rate transform vs diff dist = {}, {}, {}'.format(count_diff_transform/(count_diff_word_dist+count_diff_transform), threshold, threshold3))