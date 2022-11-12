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
    source_path: str = args.file
    last_texts: list[str] = []
    last_command: str = ""

    while True:
        command: str = input("> ")

        if not command:
            if not last_command:
                print("No command provided.")
                return

            command = last_command
        else:
            last_command = command

        command_args: list[str] = command.split()
        command = command_args[0]
        del command_args[0]

        if command in ["stop", "quit", "leave", "exit"]:
            break

        if command == "debug":
            view_debug_details()
        elif command == "generate":
            try:
                amount: int = 1 if not command_args else int(command_args[0])
            except ValueError:
                print("Argument for 'generate' must be a number.")
                continue

            if amount < 1:
                print("Amount for 'generate' must be greater than 1.")
                continue

            last_texts = []

            for _ in range(amount):
                text: str = mctg.generate().title()
                last_texts.append(text)
                print(text)
        elif command == "settings":
            config.show_settings()
        elif command == "resample":
            if command_args:
                source_path = command_args[0]

            try:
                mctg.sample_file(source_path)
            except OSError:
                print(f"Couldn't open file at '{source_path}'.")

            print(
                f"Input file '{source_path}' sampled"
                f" ({mctg.samples_analysed} samples analysed)."
            )
        elif command == "forward":
            if not last_texts:
                print("No text to forward.")
                continue

            mctg.sample_texts(last_texts, average=True)

            print(f"Sampled {len(last_texts)} samples.")

            try:
                with open(source_path, "a", encoding="utf_8") as samples_file:
                    samples_file.write("\n".join(last_texts) + "\n")
            except OSError:
                print(f"Couldn't open file at '{source_path}'.")
                continue

            print(f"Forwarded {len(last_texts)} samples to '{source_path}'.")
        else:
            print(f"Command '{command}' not recognized.")


try:
    mctg.sample_file(args.file)
except OSError:
    print(f"Couldn't open file at '{args.file}'.")
    exit()

print(
    f"Input file '{args.file}' sampled"
    f" ({mctg.samples_analysed} samples analysed)."
)

interpreter()
