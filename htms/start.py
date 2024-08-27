import sys
from htms.HTMSParser import HTMSParser


if __name__ == "__main__":
    # get first parameter from command line
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        print(f"Usage: {sys.argv[0]} <file.html>")
        sys.exit(1)

    # read the file
    with open(file_name, "r") as f:
        sample_html = f.read()
        print(f"Loaded html from '{file_name}'")

    parser = HTMSParser()
    parser.feed(sample_html)
    parser.start()
