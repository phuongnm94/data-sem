def preprocess(file_path: str, out_folder="../ms_pars/", type_data="train"):
    samples = {"x": [],
               "y": []}
    with open(file_path, encoding="utf8", mode="rt") as f:
        full_lines = [l.strip() for l in f.readlines()]
        tmp_sample = {"x": None, "y": None, "parameters": []}
        for l in full_lines:
            if l.startswith("="):
                param_vs = tmp_sample["parameters"]
                for param_v in param_vs:
                    if param_v is not None:
                        param_v_new = param_v.replace("_", " ")
                        tmp_sample["y"] = ((" " + tmp_sample["y"] + " ").replace(" " + param_v + " ",
                                                                                 " " + param_v_new + " ")).strip()
                samples["x"].append(tmp_sample["x"])
                samples["y"].append(tmp_sample["y"])
                tmp_sample = {"x": None, "y": None, "parameters": []}
            else:
                v = l.split("\t")[-1]
                if l.startswith("<question id"):
                    tmp_sample["x"] = v
                elif l.startswith("<logical"):
                    tmp_sample["y"] = v
                elif l.startswith("<parameters"):
                    tmp_sample["parameters"] = [x.strip().split(" ")[0] for x in v.split("|||")]
    with open("{}/X_{}_5.tsv".format(out_folder, type_data), encoding="utf8", mode="wt") as f:
        f.write("\n".join(samples["x"]))
    with open("{}/Y_{}_5.tsv".format(out_folder, type_data), encoding="utf8", mode="wt") as f:
        f.write("\n".join(samples["y"]))
    return


if __name__ == "__main__":
    path_data = "../MSParS/data/"
    data_name = [
        "MSParS.dev",
        "MSParS.test",
        "MSParS.train",
        "MSPars.hardtest",
    ]

    for name in data_name:
        full_path = path_data + name
        type_data = name.split(".")[-1]

        preprocess(full_path, type_data=type_data)
