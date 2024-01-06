import pandas as pd
import argparse
import json


def parse_string_list(string_list: str) -> list[str]:
    return [token[1:-1] for token in string_list[1:-1].replace(" , ", "; ").split(", ")]


def to_string_list(string_list: list[str]) -> str:
    return str(string_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a CSV file")

    parser.add_argument("--input-file", type=str, help="Path to the input CSV file")
    parser.add_argument(
        "--categorisation-file", type=str, help="Path to the categorisation JSON file"
    )
    parser.add_argument("--output-file", type=str, help="Path to the output CSV file")

    args = parser.parse_args()

    df = pd.read_csv(args.input_file)
    print(f"Loaded {len(df)} recipes")

    with open(args.categorisation_file, "r") as f:
        categorisation = json.load(f)

    df["ingredients"] = df["ingredients"].apply(parse_string_list)
    df["ingredients"] = df["ingredients"].apply(
        lambda x: [categorisation.get(ingredient, "unknown") for ingredient in x]
    )
    bad_recipes = df[df["ingredients"].apply(lambda x: "unknown" in x)].index
    print(f"Skipping {len(bad_recipes)} bad recipes")

    df.drop(bad_recipes, inplace=True)
    df["ingredients"] = df["ingredients"].apply(to_string_list)

    df.to_csv(args.output_file, index=False)
    print(f"Saved {len(df)} recipes to {args.output_file}")
