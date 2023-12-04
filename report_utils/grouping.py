import re
import typing

IngredientGrouping = dict[str, dict[str, list[str]]]

liquid_group = [
    "liquid",
    "juice",
    "syrup",
    "tea",
    "rum",
    "cream of",
    "oil",
    "beer",
    "brandy",
    "soda",
    "liqueur",
    "wine",
    "extract",
    "nectar",
    "cider",
    "vodka",
    "brine",
    "water",
    "coffee",
    "gravy",
    "whiskey",
    "espresso",
]
soup_group = [
    "onion soup",
    "garlic soup",
    "vegetable soup",
    "cheese soup",
    "chicken soup",
    "bean soup",
    "rice soup",
    "mushroom soup",
    "tomato soup",
    "bouillon",
    "bullion",
    "broth",
    "beef soup",
]
dishes_group = [
    "scallopini",
    "ravioli",
    "hummus",
    "pierogi",
    "fries",
    "tofu",
    "tapenade",
    "pesto",
    "meatballs",
    "ramen",
    "popcorn",
    "tortellini",
    "pie filling",
    "pie",
    "paste",
    "pizza",
    "sandwich",
    "pancake",
]
sweets_group = [
    "ice cream",
    "cookie",
    "cake",
    "pudding",
    "gingerbread",
    "marmalade",
    "jell-o",
    "cand",
    "cracker",
    "gelato",
    "sorbet",
    "marshmallow",
    "milk chocolate",
    "hazelnut",
    "raisins",
    "chocolate",
    "biscuit",
    "jelly",
    "fudge",
    "caramel",
    "brownie",
]
meat_group = [
    "sausage",
    "pork",
    "chicken",
    "salami",
    "beef",
    "turkey",
    "lamb",
    "bacon",
    "kielbasa",
    "pepperoni",
    "prosciutto",
    "ham",
    "steak",
    "duck",
    "veal",
    "roast",
    "ribs",
]
fish_group = [
    "shrimp",
    "tuna",
    "sardin",
    "mackerel",
    "anchovy",
    "fish",
    "seafood",
    "shells",
    "salmon",
    "fillet",
    "crab",
    "lobster",
    "clams",
]
herbs_group = [
    "oregano",
    "herbs",
    "peppermint",
    "pepper",
    "basil",
    "chives",
    "rosemary",
    "coriander",
    "cilantro",
    "parsley",
    "cumin",
    "mint",
    "thyme",
    "bay lea",
    "leaves",
    "dill",
]
spicing_group = [
    "flavoring",
    "dressing",
    "dip",
    "vinegar",
    "jam",
    "chili",
    "jalapeno",
    "seasoning",
    "cinnamon",
    "sazon",
    "honey",
    "salt",
    "sugar",
    "cocoa",
    "chile",
    "molasses",
    "vanilla",
    "spice",
    "marinade",
    "horseradish",
    "curry",
]
sauce_group = [
    "salsa",
    "mustard",
    "ketchup",
    "mayonnaise",
    "soy sauce",
    "tomato sauce",
    "pepper sauce",
    "tabasco sauce",
    "marinara sauce",
    "spaghetti sauce",
    "cheese sauce",
    "hot sauce",
    "garlic sauce",
    "barbecue sauce",
    "taco sauce",
    "bean sauce",
    "steak sauce",
    " picante sauce",
]
vegetables_group = [
    "potato",
    "beans",
    "garlic",
    "onion",
    "tomato",
    "ginger",
    "mushroom",
    "carrot",
    "peas",
    "eggplant",
    "olive",
    "pickle",
    "avocado",
    "cabbage",
    "lettuce",
    "celery",
    "spinach",
    "broccoli",
    "cauliflower",
    "bean",
    "zucchini",
    "radish",
    "vegetable",
    "corn",
    "cucumber",
    "beet",
    "caper",
    "artichoke",
    "greens",
    "squash",
    "pumpkin",
    "salad",
    "asparagus",
    "lentils",
    "soy",
    "pea",
    "paprika",
    "scallops",
]
fruits_group = [
    "coconut",
    "blueberr",
    "strawberr",
    "mango",
    "pear",
    "cherr",
    "pineapple",
    "peach",
    "orange",
    "banana",
    "apricot",
    "lemon",
    "apple",
    "raspberr",
    "fruit",
    "lime",
    "grape",
    "cranberr",
    "berr",
    "plum",
    "fig",
    "melon",
]
nuts_group = [
    "peanuts",
    "sesame",
    "almonds",
    "walnuts",
    "pecan",
    "nuts",
    "seed",
    "almond",
    "grain",
    "cardamom",
]
dairy_group = [
    "yoghurt",
    "yogurt",
    "milk",
    "feta",
    "parmesan",
    "cheddar",
    "cheese",
    "sour cream",
    "mascarpone",
    "whipped",
]
others_group = [
    "foil",
    "gelatin",
    "baking soda",
    "paper",
    "butter",
    "marrow",
    "margarine",
    "yeast",
]
bakary_group = [
    "tortilla",
    "gnocchi",
    "bread",
    "flour",
    "cereal",
    "granola",
    "rice",
    "noodle",
    "macaroni",
    "pasta",
    "linguine",
    "oats",
    "wheat",
    "pastry",
    "flakes",
    "pretzel",
    "croissant",
    "spaghetti",
    "couscous",
]
egg_group = ["egg"]
groups = {
    "others_group": others_group,
    "sauce_group": sauce_group,
    "liquid_group": liquid_group,
    "soup_group": soup_group,
    "dishes_group": dishes_group,
    "sweets_group": sweets_group,
    "meat_group": meat_group,
    "fish_group": fish_group,
    "herbs_group": herbs_group,
    "spicing_group": spicing_group,
    "vegetables_group": vegetables_group,
    "fruits_group": fruits_group,
    "nuts_group": nuts_group,
    "dairy_group": dairy_group,
    "bakary_group": bakary_group,
    "egg_group": egg_group,
    "uncategorized": ["uncategorized"],
}


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
    ingredients: typing.Iterable[str], groups: dict[str, typing.Iterable[str]] = groups
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
