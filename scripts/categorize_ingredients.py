import os
import json
import argparse
import asyncio
import math
import itertools

import dotenv
import openai
import pandas as pd

PROMPT = """
You will receive a list of ingredients separated by newlines.
For each ingredient, categorize it to higher level category. Some examples are:
- "1 cup of milk" -> "milk"
- "boneless chicken breast" -> "chicken"
- "low-fat low-sodium condensed cream of tomato soup" -> "tomato soup
Reduce number of non-essensial words as much as possible.
If an ingredient is already categorized, leave it as is.
If you can't categorize an ingredient, mark it as "unknown".

Return a VALID json (parsable) object with the following format:
{
    "ingredient": "category",
    ...
}
"""
SYSTEM_MESSAGE = {"role": "system", "content": PROMPT}


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
        "--input", type=str, required=True, help="Path to input recipies CSV file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="categorized.json",
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


async def categorize_ingredients(
    batch: tuple[int, list[str]], client: openai.AsyncOpenAI, model: str
) -> dict[str, str]:
    print(f"Processing batch {batch[0]}")
    idx, ingredients = batch
    batch_content = "\n".join(ingredients)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            SYSTEM_MESSAGE,
            {"role": "user", "content": batch_content},
        ],
    )
    content = (
        response.choices[0]
        .message.content.strip()
        .removeprefix("```json\n")
        .removesuffix("\n```")
    )
    print(f"Batch {idx} completed")
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        dump_bad_response(content, idx, e)
        return {}


async def process_batches(
    batches: list[tuple[int, list[str]]], client: openai.AsyncOpenAI, model: str
) -> list[dict[str, str]]:
    tasks = []
    for batch in batches:
        tasks.append(categorize_ingredients(batch, client, model))
    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    args = setup_args()

    dotenv.load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("No API key found. Please set OPENAI_API_KEY in .env file.")
        exit(1)

    recipies_df = pd.read_csv(args.input)
    ingredients = tuple(
        set(
            itertools.chain.from_iterable(
                recipies_df["ingredients"].apply(parse_string_list)
            )
        )
    )
    batch_size = args.batch_size
    model = args.model
    num_ingredients = len(ingredients)
    num_batches = math.ceil(num_ingredients / batch_size)

    print(f"Found {len(ingredients)} ingredients")
    print(f"Will result in {num_batches} batches of size {batch_size}")

    client = openai.AsyncOpenAI(api_key=api_key)
    work_batches = enumerate(batches(ingredients, batch_size))
    result = asyncio.run(
        process_batches(work_batches, client, model),
    )
    joint_result = {k: v for d in result for k, v in d.items()}
    with open(args.output, "w") as f:
        json.dump(joint_result, f)
    print("Exported to", args.output)
