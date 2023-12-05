import re
import typing

IngredientGrouping = dict[str, dict[str, list[str]]]


def create_formula(words: list[str]) -> str:
    formula = ""
    for word in words:
        formula += "|" + word
    return formula[1:]


def split_ingriedents(word: str, formula: str) -> list[str]:
    return re.split(formula, word)


def is_part_of_group(group: str, ingredient: str) -> bool:
    group_is_multiword = group.count(" ") > 0
    if group_is_multiword:
        if group in ingredient or group == ingredient:
            return True
        is_matching = True
        for word in group:
            if word not in ingredient:
                is_matching = False
        return is_matching

    for token in ingredient.split(" "):
        if group in token and group[0] == token[0]:
            return True

    return False


def initialize_grouping(groups: dict[str, list[str]]) -> IngredientGrouping:
    ingredient_map = {}
    for group, sub_groups in groups.items():
        ingredient_map[group] = {}
        for sub_group in sub_groups:
            ingredient_map[group][sub_group] = []
    return ingredient_map


def group_ingredients(
    ingredients: typing.Iterable[str], groups: dict[str, typing.Iterable[str]]
) -> IngredientGrouping:
    map_groups = initialize_grouping(groups)
    for ingredient in ingredients:
        added = False
        for group, sub_groups in groups.items():
            for sub_group in sub_groups:
                if is_part_of_group(sub_group, ingredient):
                    map_groups[group][sub_group].append(ingredient)
                    added = True
                    break
            if added:
                break
        else:
            map_groups["uncategorized"]["uncategorized"].append(ingredient)
    return map_groups


def invert_grouping(grouping: IngredientGrouping) -> dict[str, list[str]]:
    return {
        val: key
        for group in grouping
        for key, lst in grouping[group].items()
        for val in lst
    }
