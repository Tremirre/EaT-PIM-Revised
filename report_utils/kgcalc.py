import numpy as np

from typing import Iterable

from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeGraphCalculator:
    """
    Calculator for performing operations and similarity calculations on knowledge graph embeddings.
    """

    def __init__(
        self,
        entity_embeddings: np.ndarray,
        entity_id_mapping: dict[str, int],
        relation_embeddings: np.ndarray,
        relation_id_mapping: dict[str, int],
    ):
        self.entity_embeddings = entity_embeddings
        self.entity_id_mapping = entity_id_mapping
        self.id_to_entity = {v: k for k, v in entity_id_mapping.items()}
        self.relation_embeddings = relation_embeddings
        self.relation_id_mapping = relation_id_mapping
        self.id_to_relation = {v: k for k, v in relation_id_mapping.items()}

    def _transE_calculation(
        self, ops: dict | np.ndarray, rem_ing: str, rep_ing: str | None = None
    ) -> np.ndarray:
        if not isinstance(ops, dict):
            if ops == rem_ing and rep_ing is not None:
                ops = rep_ing
            head = self.entity_embeddings[self.entity_id_mapping[ops]]
            return head

        relation_name, entity_list = next(iter(ops.items()))

        relation = self.relation_embeddings[self.relation_id_mapping[relation_name]]

        entity_list_mod = [
            self._transE_calculation(ent, rem_ing, rep_ing) for ent in entity_list
        ]
        head_content = np.mean(np.array(entity_list_mod), axis=0)
        stacked_score = head_content + relation

        return stacked_score

    def calculate_ingredient_output_similarity(
        self,
        recipe_ops: dict | np.ndarray,
        replace_ing: str,
        all_ingredients: Iterable[str],
    ) -> tuple[np.ndarray, np.ndarray]:
        original_calc_vec = self._transE_calculation(recipe_ops, replace_ing)
        calculated_sim_vec = np.zeros(len(all_ingredients))
        for i, ing in enumerate(all_ingredients):
            calc_recipe_vec = self._transE_calculation(recipe_ops, replace_ing, ing)

            calculated_sim_vec[i] = cosine_similarity(
                original_calc_vec.reshape(1, -1), calc_recipe_vec.reshape(1, -1)
            )[0][0]
        return calculated_sim_vec

    def calculate_recipe_output_similarity(
        self,
        target_recipe: str,
        recipe_ops: dict | np.ndarray,
        replace_ing: str,
        all_ingredients: Iterable[str],
    ) -> tuple[np.ndarray, np.ndarray]:
        original_recipe_vec = self.entity_embeddings[
            self.entity_id_mapping[target_recipe]
        ]
        recipe_output_vec = np.zeros(len(all_ingredients))
        for i, ing in enumerate(all_ingredients):
            calc_recipe_vec = self._transE_calculation(recipe_ops, replace_ing, ing)
            recipe_output_vec[i] = cosine_similarity(
                original_recipe_vec.reshape(1, -1), calc_recipe_vec.reshape(1, -1)
            )[0][0]

        return recipe_output_vec

    def calculate_individual_ingredient_similarity(
        self, target_ing: str, all_ingredients: Iterable[str]
    ) -> np.ndarray:
        target_ing_emb = self.entity_embeddings[self.entity_id_mapping[target_ing]]
        sims = cosine_similarity(target_ing_emb.reshape(1, -1), self.entity_embeddings)[
            0
        ]
        result = np.zeros(len(all_ingredients))
        for i, ing in enumerate(all_ingredients):
            result[i] = sims[self.entity_id_mapping[ing]]
        return result
