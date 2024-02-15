import pandas as pd
import glob
import os
import uuid


def find_relevant_csv(name, idx=None):
    joined_files = os.path.join("csv", f"{name}.csv")
    joined_list = glob.glob(joined_files)
    if idx:
        joined_list.sort(key=lambda item: int(item.split("_")[idx].split(".")[0]))
    return joined_list


def join_drop_dup(joined_list, drop_dup):
    df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)
    print(f"Before dropping duplicate : {len(df)}")

    if drop_dup:
        df = df.drop_duplicates()
    print(f"After dropping duplicate: {len(df)}")
    return df


def remove_ref_files(list):
    for file in list:
        os.remove(file)


def clean_up_n_save_new_csv(wildcard_name, idx_to_sort, new_file_name, drop_dup=True):
    bundled_file = find_relevant_csv(wildcard_name, idx_to_sort)
    print(bundled_file)
    cleaned_df = join_drop_dup(bundled_file, drop_dup)
    cleaned_df.to_csv(f"csv/{new_file_name}.csv", index=False)

    remove_ref_files(bundled_file)


def check_unique(name):
    ls = pd.read_csv(f"csv/{name}.csv")
    return ls.places.unique()


def all_unique():
    au = pd.read_csv(f"csv/cities_n_links.csv")
    return au.city.unique()


def check_not_seen(name):
    all_ls = all_unique()
    shop_ls = check_unique(name)
    not_seen = []
    for city in all_ls:
        if city not in shop_ls:
            not_seen.append(city)

    return not_seen


def amend(name, not_seen):
    links = pd.read_csv("csv/cities_n_links.csv", index_col="city")
    df = links.loc[not_seen]
    df.to_csv(f"csv/{name}_amended.csv")


def add_amend(name, file):
    not_seen = check_not_seen(file)
    print(not_seen)
    amend(name, not_seen)


def verify_len(file, amfile):
    s_a = pd.read_csv(f"csv/{file}.csv")
    s_am = pd.read_csv(f"csv/{amfile}.csv")
    print(len(s_a.places.unique()) + len(s_am.city.unique()) == len(all_unique()))


def concat_n_del(wildcard, idx, save_name):
    all_files = find_relevant_csv(wildcard, idx)
    print(all_files)
    df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)
    df.to_csv(f"csv/{save_name}.csv", index=False)
    remove_ref_files(all_files)


def add_uuid(file, col_name="id", id=None):
    df = pd.read_csv(f"csv/{file}.csv")
    if not id:
        id = [uuid.uuid4() for _ in range(len(df))]
    df.insert(0, col_name, id)
    print(df.head())
    df.to_csv(f"csv/{file}.csv", index=False)
