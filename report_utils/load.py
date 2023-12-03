import pathlib
import json

import numpy as np


def load_embedding_data(
    embedding_path: pathlib.Path,
) -> tuple[np.ndarray, np.ndarray]:
    ent_embs = np.load((embedding_path / "entity_embedding.npy").resolve())
    rel_embs = np.load((embedding_path / "relation_embedding.npy").resolve())
    return ent_embs, rel_embs


def load_graph_data(
    graph_path: pathlib.Path,
) -> dict[int, str]:
    lines = graph_path.read_text().splitlines()
    graph_data = {}
    for line in lines:
        index, value = line.strip().split("\t", 1)
        graph_data[int(index)] = value
    return graph_data


def load_json_list(
    file_path: pathlib.Path,
) -> dict[str, dict]:
    lines = file_path.read_text().splitlines()
    file_data = {}
    for line in lines:
        content = json.loads(line)
        for key, value in content.items():
            file_data[key] = value
    return file_data


if __name__ == "__main__":
    entities = load_graph_data(
        pathlib.Path("./data/recipe_parsed_sm/triple_data/entities.dict")
    )
    relations = load_graph_data(
        pathlib.Path("./data/recipe_parsed_sm/triple_data/relations.dict")
    )
    ent_embs, rel_embs = load_embedding_data(
        pathlib.Path(
            "./data/recipe_parsed_sm/models/GraphOps_recipe_parsed_sm_graph_TransE"
        )
    )
    rec = load_json_list(pathlib.Path("./data/recipe_parsed_sm/triple_data/train.txt"))
