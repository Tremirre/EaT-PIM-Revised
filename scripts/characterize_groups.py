import os
import json
import argparse
import asyncio
import math

import dotenv
import openai

PROMPT = """
You will receive a list of food groups separated by newlines.
For each group, characterize it with the following characteristics:
- "origin": "meat", "vegetable", "fruit", "grain", "dairy", "spice", "other"
- "type": "raw", "cooked", "processed"
- "state": "solid", "liquid", "powder", "other"
- "texture": "soft", "hard", "crunchy", "other"
- "taste": "sweet", "sour", "salty", "bitter", "umami", "other"
- "taste-intensity": "low", "medium", "high"
- "smell": "sweet", "sour", "salty", "bitter", "umami", "other"
- "smell-intensity": "low", "medium", "high"

Return a VALID json (parsable) object with the following format:
{
    "group": {
        "origin": "meat",
        "type": "raw",
        "state": "solid",
        "texture": "soft",
        "taste": "sweet",
        "taste-intensity": "low",
        "smell": "sweet",
        "smell-intensity": "low"
    },
    ...
}
"""
SYSTEM_MESSAGE = {"role": "system", "content": PROMPT}
TEMPERATURE = 0
SEED = 0


def setup_args():
    parser = argparse.ArgumentParser(description="Categorize ingredients")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=250,
        help="Number of ingredients to categorize at once",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo-1106",
        help="OpenAI API model to use. See https://beta.openai.com/docs/api-reference/completions/create",
    )
    parser.add_argument(
        "--input", type=str, required=True, help="Path to input JSON file with groups"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="characterized.json",
        help="Path to output JSON file",
    )
    return parser.parse_args()


def parse_string_list(string_list: str) -> list[str]:
    return [
        token[1:-1].replace('"', "")
        for token in string_list[1:-1].replace(" , ", "; ").split(", ")
    ]


def batches(lst: list, batch_size: int) -> list[list]:
    return (lst[i : i + batch_size] for i in range(0, len(lst), batch_size))


def dump_bad_response(content: str, idx: int, e: Exception):
    path = os.path.join(os.path.dirname(__file__), "failed")
    result_path = os.path.join(path, f"result-{idx}.txt")
    exception_path = os.path.join(path, f"exception-{idx}.txt")
    with open(result_path, "w") as f:
        f.write(content)
    with open(exception_path, "w") as f:
        f.write(str(e))


async def characterize_groups(
    batch: tuple[int, list[str]], client: openai.AsyncOpenAI, model: str
) -> dict[str, str]:
    print(f"Processing batch {batch[0]}")
    idx, groups = batch
    batch_content = "\n".join(groups)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            SYSTEM_MESSAGE,
            {"role": "user", "content": batch_content},
        ],
        seed=SEED,
        temperature=TEMPERATURE,
    )
    content = response.choices[0].message.content.strip()
    start_idx = content.find("{")
    end_idx = content.rfind("}")
    json_content = content[start_idx : end_idx + 1]
    print(f"Batch {idx} completed")
    try:
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON found")
        return json.loads(json_content)
    except (json.JSONDecodeError, ValueError) as e:
        dump_bad_response(content, idx, e)
        return {}


async def process_batches(
    batches: list[tuple[int, list[str]]], client: openai.AsyncOpenAI, model: str
) -> list[dict[str, str]]:
    tasks = []
    for batch in batches:
        tasks.append(characterize_groups(batch, client, model))
    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    args = setup_args()

    dotenv.load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("No API key found. Please set OPENAI_API_KEY in .env file.")
        exit(1)

    with open(args.input) as f:
        groups = json.load(f)

    batch_size = args.batch_size
    model = args.model
    num_ingredients = len(groups)
    num_batches = math.ceil(num_ingredients / batch_size)

    print(f"Found {len(groups)} ingredients")
    print(f"Will result in {num_batches} batches of size {batch_size}")

    client = openai.AsyncOpenAI(api_key=api_key)
    work_batches = enumerate(batches(groups, batch_size))
    result = asyncio.run(
        process_batches(work_batches, client, model),
    )
    joint_result = {k: v for d in result for k, v in d.items()}
    with open(args.output, "w") as f:
        json.dump(joint_result, f)
    print("Exported to", args.output)