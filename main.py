from reverse_data import save_definitions
from reverse_data import Entry, WordDictionary
import os
import json
import re
from tqdm import tqdm

from bs4 import BeautifulSoup as BS

DICTIONARY_PATH = "./asset/Body.data"
OUTPUT_PATH = "./output/test.html"

ls = []


def cache_the_dictionary_to_json(dictionary_path):
    if not dictionary_path.endswith('Body.data'):
        raise ValueError(f'Expected a Body.data file, got {dictionary_path}')

    word_dict = WordDictionary.from_file(dictionary_path)

    # d_list = []
    # links_list = []
    # for _, entry in word_dict.d.items():
    #     d_list.append({"key": entry.key, "content": entry.content})
    #
    # for _, entry in word_dict.links.items():
    #     links_list.append({"key": entry.key, "content": entry.content})
    #
    # json_dict = {"d": d_list, "links": links_list}
    # with open("./cache/cache.json", "w") as json_file:
    #     json.dump(json_dict, json_file, indent=4)

    file = open("./cache/output.txt", "w")

    jlist = []
    # the_pass = []
    pattern = r'^[a-zA-Z\-]+$'
    for _, entry in tqdm(word_dict.d.items()):
        flag = True
        if re.match(pattern, entry.key):
            res = hendel_entry_str(entry.content)
            if res is not None:
                jlist.append(res)
                flag = False
        if flag:
            # the_pass.append(entry.key)
            file.write(entry.key + "\n")

    print(len(jlist))
    json_dict = {"d": jlist}
    with open("./cache/cache.json", "w") as json_file:
        json.dump(json_dict, json_file, indent=4)
        pass

    # with open("./output.txt", "w") as file:
    #     for string in the_pass:
    #         file.write(string + "\n")
    file.close()

    print("For DEBUG")


def hendel_entry_str(str):
    # res = {
    #     "wd": "word",
    #     "mn": [ {"ps": "n", "trans": "解释"}
    #
    #     ]
    # }
    soup = BS(str, 'html.parser')

    wds = soup.find_all("span", class_='hw')
    if len(wds) == 0:
        return None
    wd = wds[0].text.strip()

    mns = soup.select('span.gramb.x_xd0')  # 避免少匹配了
    if len(mns) == 0:
        return None

    mns = mns[0: min(4, len(mns))]
    mn = []
    for m in mns:
        ps = m.find("span", class_='ps')
        tss1 = m.find_all("span", class_="trg x_xd2")
        tss2 = m.find_all("span", class_="trgg x_xd2")
        tss = tss1 + tss2
        if len(tss) == 0:
            continue

        tss = tss[0: min(4, len(tss))]
        trans = []
        for ts in tss:
            trs = ts.select('span.trans:not(.ty_pinyin)')  # 避免匹配class="trans ty_pinyin
            for t in trs:
                trans.append(t.text.strip())
        if len(trans) == 0:
            continue

        mn.append({"ps": ci_xing(ps), "trans": " ".join(trans)})

    if len(mn) == 0:
        return None

    res = {"wd": wd, "mn": mn}
    return res


def ci_xing(str):
    if str is None:
        return ""

    str = str.text.strip()
    if "noun" in str:
        return "n."

    if "verb" in str:
        if "intransitive" in str:
            return "vi."
        elif "transitive" in str:
            return "vt."
        else:
            return "v."

    if "adjective" in str:
        return "adj."

    if "adverb" in str:
        return "adv."

    if "preposition" in str:
        return "prep."

    return ""


def generate_my_word():
    wl = []
    with open("./input.txt", 'r') as file:
        for line in file:
            wl.append(line.strip())
    swl = sorted(wl)  # 排序为了匹配字典
    with open('./cache/org_dictionary.json', 'r', encoding='utf-8') as json_file:
        jdata = json.load(json_file)

    dict_wl = []
    for item in jdata['d']:
        dict_wl.append(item["wd"])

    print("If there are something below, Warning!")
    for w in swl:
        if w in dict_wl:
            pass
        else:
            print(w)

    jdict = {"wl": []}
    jwl = []

    if os.path.exists("./output/word_list.json"):
        jfile = open("./output/word_list.json", "r")
        jd = json.load(jfile)
        jdict["wl"] = jd["wl"]
        for item in jdict["wl"]:
            jwl.append(item["word"])
        jfile.close()

    count_idx = len(jdict["wl"])
    for w in wl:
        if w in jwl:
            pass
        else:
            jdict["wl"].append({"idx": count_idx, "word": w, "isknown": False})
            count_idx += 1

    with open("./output/word_list.json", "w") as json_file:
        json.dump(jdict, json_file, indent=4)
        pass


def simplify_dictionary():
    wl = []
    with open("./input.txt", 'r') as file:
        for line in file:
            wl.append(line.strip())
    swl = sorted(wl)  # 排序为了匹配字典

    with open('./cache/org_dictionary.json', 'r', encoding='utf-8') as json_file:
        jdata = json.load(json_file)

    sp_dict = {"d": []}

    dict_wl = []
    mem_dict = {}
    for item in jdata['d']:
        dict_wl.append(item["wd"])
        mem_dict[item["wd"]] = item["mn"]

    print("If there are something below, Warning!")
    for w in swl:
        if w in dict_wl:
            sp_dict["d"].append({"wd": w, "mn": mem_dict[w]})
        else:
            print(w)

    with open("./output/dictionary.json", "w") as json_file:
        json.dump(sp_dict, json_file, indent=4)
        pass


if __name__ == '__main__':
    # save_definitions(DICTIONARY_PATH, ["significant", "test", "abatement", "record", "is"], OUTPUT_PATH)
    # cache_the_dictionary_to_json(DICTIONARY_PATH)
    generate_my_word()
    # simplify_dictionary()
