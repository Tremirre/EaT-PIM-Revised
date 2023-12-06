import dataclasses
import collections
import itertools
import networkx as nx

PREDICATE_PREFIX = "pred_"


@dataclasses.dataclass
class RecipeData:
    graph: nx.DiGraph
    ingredients: set[str]

    def ingredient_actions(self, ingredient: str) -> set[str]:
        if ingredient not in self.ingredients:
            raise ValueError(f"Ingredient {ingredient} not in recipe")
        return {
            node.split("_")[1]
            for node in nx.dfs_successors(self.graph, ingredient).keys()
            if node != ingredient
        }


def parse_graph_tree(
    graph_tree: dict, valid_ingredients: set[str]
) -> dict[str, RecipeData]:
    recipes = {}
    for recipe, graph_data in graph_tree.items():
        graph = nx.DiGraph()
        graph.add_edges_from(graph_data["edges"])
        ingredients = {
            node
            for node in graph.nodes()
            if not node.startswith(PREDICATE_PREFIX) and node in valid_ingredients
        }
        recipes[recipe] = RecipeData(graph=graph, ingredients=ingredients)
    return recipes


def get_ingredient_usage_counts_from_recipies(
    all_recipes: dict[str, RecipeData]
) -> collections.Counter[str, int]:
    counts = collections.Counter(
        itertools.chain.from_iterable(
            recipe.ingredients for recipe in all_recipes.values()
        )
    )
    return counts


if __name__ == "__main__":
    import json

    with open("./data/recipe_parsed_sm/ingredient_list.json") as f:
        ingredients = set(json.load(f))

    with open("./data/recipe_parsed_sm/recipe_tree_data.json") as f:
        graph_tree = json.load(f)

    recipes = parse_graph_tree(graph_tree, ingredients)
    counts = collections.Counter(
        itertools.chain.from_iterable(recipe.ingredients for recipe in recipes.values())
    )
    print("Usage count:", sum(counts.values()))
