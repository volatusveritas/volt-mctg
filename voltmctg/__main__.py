from pprint import pprint
from argparse import ArgumentParser
from sys import exit

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

    try:
        with open(path, encoding="utf_8") as sample_file:
            for line in sample_file:
                mctg.sample_text(line)
    except OSError as e:
        print(f"Couldn't open file at '{path}'.")
        raise e

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
    last_command: str = ""

    while True:
        command: str = input("> ")

        if not command:
            if not last_command:
                print("No command provided.")
                return

            command = last_command

        command_args: list[str] = command.split()
        command = command_args[0]
        del command_args[0]

        last_command = command

        if command in ["stop", "quit", "leave", "exit"]:
            break

        if command == "debug":
            view_debug_details()
        elif command.startswith("generate"):
            amount: int = 1 if not command_args else int(command_args[0])

            for _ in range(amount):
                print(mctg.generate().title())
        elif command == "settings":
            config.show_settings()
        elif command == "resample":
            target_path: str

            if not command_args:
                target_path = args.file
                print("Using source provided at initialization.")
            else:
                target_path = command_args[0]

            try:
                sample_input_file(target_path)
            except OSError:
                pass
        else:
            print(f"Command '{command}' not recognized.")


try:
    sample_input_file(args.file)
except OSError:
    exit()

interpreter()
