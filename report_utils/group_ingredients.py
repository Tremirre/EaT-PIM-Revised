import re


def create_formula(words):
    formula = ""
    for i in words:
        formula = formula + "|" + i
    return formula[1:]


def split_ingriedents(word, formula):
    return re.split(formula, word)


def sort_dict(dict):
    return sorted(dict.items(), key=lambda x: x[1], reverse=True)


def check_matching(word, sentence):
    if len(word.split(" ")) == 1:
        for i in sentence.split(" "):
            if word in i and word[0] == i[0]:
                return True
        return False
    return word in sentence


def create_map(groups):
    map_groups = {}
    for key, value in groups.items():
        map_groups[key] = {}
        for i in value:
            map_groups[key][i] = []
    return map_groups
