import json
import pathlib
import enum

import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity

from report_utils import load, graph, similarity, kgcalc

INGREDIENTS_FILE = "ingredient_list.json"
RECIPES_FILE = "recipe_tree_data.json"
ENTITIES_FILE = "entities.dict"
RELATIONS_FILE = "relations.dict"
EXTRA_MODEL_DATA_FOLDER = "triple_data"


class SimilarityMetric(enum.Enum):
    SIMPLE_COSINE = enum.auto()
    TARGET_COSINE = enum.auto()
    INGREDIENT_OUTPUT = enum.auto()
    RECIPE_OUTPUT = enum.auto()
    INDIVIDUAL_INGREDIENT = enum.auto()
    METADATA_WEIGHTED = enum.auto()


class Recommender:
    def __init__(
        self,
        path_to_recommender_data: str,
        model: str,
        path_to_categorisation: str,
        path_to_metadata: str,
        metadata_weights: dict[str, float],
    ) -> None:
        self.path_to_recommender_data = pathlib.Path(path_to_recommender_data).resolve()
        self.model = model
        self.path_to_categorisation = pathlib.Path(path_to_categorisation).resolve()
        self.path_to_metadata = pathlib.Path(path_to_metadata).resolve()
        self.metadata_weights = metadata_weights
        self._load_data()

    def evaluate_substitutes(
        self,
        ingredient: str,
        similarity_metric: SimilarityMetric,
        recipe_id: int,
    ) -> np.ndarray:
        operation_recipe_key = f"RECIPE_OUTPUT_{recipe_id}"
        match similarity_metric:
            case SimilarityMetric.SIMPLE_COSINE:
                return similarity.get_cosine_similarities(
                    self.cooc_matrix, self.ingredient_index_maping[ingredient]
                )
            case SimilarityMetric.TARGET_COSINE:
                target_recipe_vector = similarity.get_recipe_ingredients_vector(
                    self.recipe_data[recipe_id].ingredients,
                    self.ingredient_index_maping,
                )
                return similarity.get_cosine_similarities_on_target_ingredients(
                    cooccurence_matrix=self.cooc_matrix,
                    ingredient_counts=self.ingredient_counts_vector,
                    recipe_ingredients=target_recipe_vector,
                    target_idx=self.ingredient_index_maping[ingredient],
                )
            case SimilarityMetric.INGREDIENT_OUTPUT:
                return self.kg_calculator.calculate_ingredient_similarity(
                    target_recipe=operation_recipe_key,
                    recipe_ops=self.operations[operation_recipe_key],
                    replace_ing=ingredient,
                    ing_list=tuple(self.usage_counts.keys()),
                )[0]
            case SimilarityMetric.RECIPE_OUTPUT:
                return self.kg_calculator.calculate_ingredient_similarity(
                    target_recipe=operation_recipe_key,
                    recipe_ops=self.operations[operation_recipe_key],
                    replace_ing=ingredient,
                    ing_list=tuple(self.usage_counts.keys()),
                )[1]
            case SimilarityMetric.INDIVIDUAL_INGREDIENT:
                return self.kg_calculator.calculate_individual_ingredient_similarity(
                    target_ing=ingredient,
                    ing_set=set(self.usage_counts.keys()),
                )
            case SimilarityMetric.METADATA_WEIGHTED:
                mapped_ingredient = self.categorisation[ingredient]
                ing_metadata_vector = self.metadata_matrix.loc[
                    mapped_ingredient
                ].to_numpy()
                metadata_similarities = cosine_similarity(
                    ing_metadata_vector.reshape(1, -1), self.metadata_matrix.to_numpy()
                ).flatten()
                result = np.zeros(len(self.usage_counts))
                for i, ingredient in enumerate(self.usage_counts.keys()):
                    mapped_ingredient = self.categorisation[ingredient]
                    result[i] = metadata_similarities[
                        self.ingredient_index_maping[mapped_ingredient]
                    ]
                return result

    def _load_data(self) -> None:
        with open(self.path_to_recommender_data / INGREDIENTS_FILE, "r") as f:
            self.ingredients = set(json.load(f))

        with open(self.path_to_recommender_data / RECIPES_FILE, "r") as f:
            self.graph_data = json.load(f)

        self.recipe_data = graph.parse_graph_tree(self.graph_data, self.ingredients)
        self.usage_counts = graph.get_ingredient_usage_counts_from_recipies(
            self.recipe_data
        )
        self.ingredient_counts_vector = np.array(
            [self.usage_counts[ingredient] for ingredient in self.usage_counts.keys()]
        )
        self.ingredient_index_maping = {
            ingredient: i for i, ingredient in enumerate(self.usage_counts)
        }
        self.cooc_matrix = similarity.calculate_cooccurence_matrix(
            (recipe.ingredients for recipe in self.recipe_data.values()),
            self.ingredient_index_maping,
        )

        self.entity_embeddings, self.relation_embeddings = load.load_embedding_data(
            self.path_to_recommender_data / "models" / self.model
        )

        self.id_to_entities = load.load_graph_data(
            self.path_to_recommender_data / EXTRA_MODEL_DATA_FOLDER / ENTITIES_FILE
        )
        self.entities = {v: k for k, v in self.id_to_entities.items()}

        self.id_to_relations = load.load_graph_data(
            self.path_to_recommender_data / EXTRA_MODEL_DATA_FOLDER / RELATIONS_FILE
        )
        self.relations = {v: k for k, v in self.id_to_relations.items()}

        self.kg_calculator = kgcalc.KnowledgeGraphCalculator(
            entity_embeddings=self.entity_embeddings,
            entity_id_mapping=self.entities,
            relation_embeddings=self.relation_embeddings,
            relation_id_mapping=self.relations,
        )

        self.operations = {}
        for dataset in ["train", "valid", "test"]:
            self.operations.update(
                load.load_json_list(
                    self.path_to_recommender_data
                    / EXTRA_MODEL_DATA_FOLDER
                    / f"{dataset}.txt"
                )
            )

        with open(self.path_to_categorisation, "r") as f:
            self.categorisation = json.load(f)

        with open(self.path_to_metadata, "r") as f:
            self.ingredients_metadata = pd.read_json(f).T

        metadata_one_hot = pd.get_dummies(self.ingredients_metadata)
        for column in metadata_one_hot.columns:
            col_group = column.split("_")[0]
            metadata_one_hot[column] *= self.metadata_weights[col_group]

        other_columns = [col for col in metadata_one_hot.columns if "other" in col]
        self.metadata_matrix = metadata_one_hot.drop(columns=other_columns)
