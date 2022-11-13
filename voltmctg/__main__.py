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
                print("Amount for 'generate' must be greater than 0.")
                continue

            last_texts = []

            for i in range(amount):
                text: str = mctg.generate().title()
                last_texts.append(text)
                print((f"[{i + 1}] " if amount > 1 else "") + text)
        elif command == "settings":
            if not command_args:
                config.show_settings()
                continue

            if len(command_args) == 1:
                try:
                    print(
                        f"{command_args[0]}"
                        f" is {getattr(config, command_args[0])}."
                    )
                except AttributeError:
                    print(f"Setting {command_args[0]} not found.")

                continue

            if len(command_args) == 3 and command_args[1] == "=":
                try:
                    getattr(config, command_args[0])
                except AttributeError:
                    print(f"Setting '{command_args[0]}' not found.")
                else:
                    try:
                        setattr(config, command_args[0], eval(command_args[2]))
                    except:
                        print(f"Unable to parse value '{command_args[2]}'.")
                    else:
                        print(
                            f"Setting {command_args[0]}"
                            f" set to {command_args[2]}."
                        )

                continue

            for setting in command_args:
                try:
                    print(f"{setting} is {getattr(config, setting)}")
                except AttributeError:
                    print(f"Setting '{setting}' not found.")
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

            targets: list[str]

            if not command_args or command_args[0] == "all":
                targets = last_texts
            else:
                targets = []

                for arg in command_args:
                    try:
                        idx: int = int(arg) - 1
                    except ValueError:
                        print(
                            f"Not possible to convert '{arg}' to an integer."
                        )
                        continue

                    try:
                        targets.append(last_texts[idx])
                    except IndexError:
                        print(f"Couldn't find item at index '{idx + 1}'.")
                        continue

            mctg.sample_texts(targets, average=True)
            print(f"Sampled {len(targets)} samples.")

            try:
                with open(source_path, "a", encoding="utf_8") as samples_file:
                    samples_file.write("\n".join(targets) + "\n")
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
