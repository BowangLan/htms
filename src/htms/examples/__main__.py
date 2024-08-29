import sys
import os
from pathlib import Path
from rich import print

from htms.HTMSLParser import HTMSParser


def get_example_files():
    examples = []
    for file in os.listdir(Path(__file__).parent / "../../../example_html"):
        if file.endswith(".html"):
            examples.append(file)
    return examples


def main():
    example_files = get_example_files()

    if len(sys.argv) < 2:
        print("Usage: htms <file.html>")
        print("Examples:")
        for example in get_example_files():
            print(f"  python -m htms.examples {example}")
        return

    file_name = sys.argv[1]

    if file_name not in example_files:
        print(f"File '{file_name}' not found in example_html")
        return

    file_path = Path(__file__).parent / "../../../example_html" / file_name
    with open(file_path, "r") as f:
        sample_html = f.read()
        print(f"Loaded html from '{file_name}'")

    parser = HTMSParser()
    parser.feed(sample_html)
    parser.start()


if __name__ == "__main__":
    main()
