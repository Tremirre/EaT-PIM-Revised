import numpy as np

from functools import cache

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

    def calculate_ingredient_similarity(
        self,
        target_recipe: str,
        recipe_ops: dict | np.ndarray,
        replace_ing: str,
        ing_list: tuple[str],
    ) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
        original_calc_vec = self._transE_calculation(recipe_ops, replace_ing)
        original_recipe_vec = self.entity_embeddings[
            self.entity_id_mapping[target_recipe]
        ]
        calculated_sim = {}
        original_sim = {}
        for ing in ing_list:
            calc_recipe_vec = self._transE_calculation(recipe_ops, replace_ing, ing)

            calculated_sim[ing] = cosine_similarity(
                original_calc_vec.reshape(1, -1), calc_recipe_vec.reshape(1, -1)
            )[0][0]
            original_sim[ing] = cosine_similarity(
                original_recipe_vec.reshape(1, -1), calc_recipe_vec.reshape(1, -1)
            )[0][0]

        sorted_sim_to_calc = sorted(
            calculated_sim.items(), key=lambda x: x[1], reverse=True
        )
        sorted_sim_to_og = sorted(
            original_sim.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_sim_to_calc, sorted_sim_to_og

    def calculate_individual_ingredient_similarity(
        self, target_ing: str, ing_set: set[str]
    ) -> list[tuple[str, float]]:
        target_ing_emb = self.entity_embeddings[self.entity_id_mapping[target_ing]]
        sims = cosine_similarity(target_ing_emb.reshape(1, -1), self.entity_embeddings)[
            0
        ]

        sim_dict = {
            self.id_to_entity[i]: sims[i]
            for i in range(len(sims))
            if self.id_to_entity[i] in ing_set
        }

        sorted_sim = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_sim
