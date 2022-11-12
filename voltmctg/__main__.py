from pprint import pprint
from argparse import ArgumentParser

from voltmctg.config import Config
from voltmctg.markov_chain_text_generator import MarkovChainTextGenerator


argparser: ArgumentParser = ArgumentParser(
    prog="voltmctg"
)

argparser.add_argument("file", help="sample strings from FILE")
argparser.add_argument(
    "-w", "--warnings",
    help="enable warnings",
    action="store_true"
)
argparser.add_argument(
    "-c", "--case-sensitive",
    help="react to casing in the samples",
    action="store_true"
)
argparser.add_argument(
    "-d", "--debug",
    help="enable debug mode",
    action="store_true"
)
argparser.add_argument(
    "-m", "--max-markov-size",
    help="size limit for markov sampling",
    type=int
)

args = argparser.parse_args()

config: Config = Config()
config.from_args(args)

mctg: MarkovChainTextGenerator = MarkovChainTextGenerator(config)


def sample_input_file(path: str) -> None:
    mctg.reset_state()

    with open(path, encoding="utf_8") as sample_file:
        for line in sample_file:
            mctg.sample_text(line)

    mctg.average_metrics()

    print(
        f"Input file sampled ({mctg.samples_analysed} samples analysed)."
    )


def view_debug_details() -> None:
    print(f"Samples analysed: {mctg.samples_analysed}")
    print(f"Average size: {mctg.average_size}")
    print(f"    min: {mctg.min_size}")
    print(f"    max: {mctg.max_size}")
    print("Starting characters:")
    pprint(mctg.starting_characters)
    print("Mappings:")
    pprint(mctg.mappings)


def interpreter() -> None:
    while True:
        command = input("> ")

        if command in ["stop", "quit", "leave", "exit"]:
            break

        if command == "debug":
            view_debug_details()
        elif command.startswith("generate"):
            args: list[str] = command.split()
            amount: int = 1 if len(args) < 2 else int(args[1])

            for _ in range(amount):
                print(mctg.generate().title())
        elif command == "settings":
            config.show_settings()
        else:
            print(f"Command '{command}' not recognized.")


try:
    sample_input_file(args.file)
    interpreter()
except OSError:
    print("Couldn't open file at path provided in argument 1.")
