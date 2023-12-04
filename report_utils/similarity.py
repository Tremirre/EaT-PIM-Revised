import numpy as np

from typing import Iterable

from sklearn.metrics.pairwise import cosine_similarity


def get_recipe_ingredients_vector(
    ingredients: set[str], index_mapping: dict[str, int]
) -> np.ndarray:
    vector = np.zeros(len(index_mapping), dtype=int)
    for ingredient in ingredients:
        vector[index_mapping[ingredient]] = 1
    return vector


def calculate_cooccurence_matrix(
    ingredients: Iterable[set[str]], index_mapping: dict[str, int]
) -> dict[str, dict[str, int]]:
    matrix = np.zeros((len(index_mapping), len(index_mapping)), dtype=int)
    for ingredient_set in ingredients:
        for ingredient in ingredient_set:
            for other_ingredient in ingredient_set:
                if ingredient != other_ingredient:
                    matrix[
                        index_mapping[ingredient], index_mapping[other_ingredient]
                    ] += 1
    return matrix


def get_cosine_similarities(
    cooccurence_matrix: np.ndarray, target_idx: int
) -> np.ndarray:
    target_row = cooccurence_matrix[target_idx]
    return cosine_similarity(target_row.reshape(1, -1), cooccurence_matrix).flatten()


def get_cosine_similarities_on_target_ingredients(
    cooccurence_matrix: np.ndarray,
    ingredient_counts: np.ndarray,
    recipe_ingredients: np.ndarray,
    target_idx: int,
) -> np.ndarray:
    ingredient_counts = ingredient_counts.reshape(-1, 1)
    prob_matrix = cooccurence_matrix / ingredient_counts
    prob_matrix *= recipe_ingredients

    return cosine_similarity(
        prob_matrix[target_idx].reshape(1, -1), prob_matrix
    ).flatten()
