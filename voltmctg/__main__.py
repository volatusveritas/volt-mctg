from pprint import pprint
from sys import argv, exit
from typing import TypeAlias
import random

from voltmctg.config import Config


config: Config = Config()


# Remove script name from args
del argv[0]


if not len(argv):
    print("Not enough arguments, please provide argument 1 (file path).")
    exit()


ChoiceMap: TypeAlias = dict[str, float]
FollowingTable: TypeAlias = dict[str, ChoiceMap]


WORD_END: str = "\0"


samples_analysed: int = 0

appearances: dict[str, int] = {}
mappings: FollowingTable = {}
starting_characters: ChoiceMap = {}

min_size: int = -1
max_size: int = -1
average_size: float = 0.0


def consider_size(size: int) -> None:
    global min_size
    global max_size
    global average_size

    if min_size == -1 or size < min_size:
        min_size = size

    if max_size == -1 or size > max_size:
        max_size = size

    average_size += size


def consider_starting_character(char: str) -> None:
    if not config.case_sensitive:
        char = char.lower()

    if not char in starting_characters:
        starting_characters[char] = 0.0

    starting_characters[char] += 1.0


def consider_segment(base: str, sequence: str) -> None:
    if not config.case_sensitive:
        base = base.lower()
        sequence = sequence.lower()

    if not base in mappings:
        appearances[base] = 0
        mappings[base] = {}

    if not sequence in mappings[base]:
        mappings[base][sequence] = 0.0

    appearances[base] += 1
    mappings[base][sequence] += 1.0


def average_metrics() -> None:
    global average_size

    # Average sizes
    average_size /= samples_analysed

    # Average starting characters
    for char in starting_characters.keys():
        starting_characters[char] /= samples_analysed

    # Average mappings
    for base in mappings.keys():
        for char in mappings[base].keys():
            mappings[base][char] /= appearances[base]


def sample_text(sample: str) -> None:
    global samples_analysed

    sample = sample[:-1] + WORD_END

    sample_size: int = len(sample)

    if sample_size < 2:
        if config.enable_warnings:
            print("[Warning] Invalid sample size found. Skipping.")

        return

    consider_size(sample_size)
    consider_starting_character(sample[0])

    for segment_size in range(1, (
        sample_size if config.max_markov_size == -1
        else min(config.max_markov_size + 1, sample_size)
    )):
        for i in range(sample_size - segment_size):
            consider_segment(
                sample[i : i + segment_size],
                sample[i + segment_size]
            )

    samples_analysed += 1


def pick_random_char(choice_map: ChoiceMap) -> str:
    threshold: float = random.random()

    for char in choice_map.keys():
        if choice_map[char] >= threshold:
            return char

        threshold -= choice_map[char]

    # NOTE: This value is never returned, this statement is for static checkers
    return ""


def generate() -> str:
    result: str = pick_random_char(starting_characters)

    if config.debug_mode:
        print("Generation steps:")
        print(result)

    while len(result) < max_size:
        selection_amount: int = 0
        selections: ChoiceMap = {}

        # for i in range(len(result), len(result) + 1):
        # BITCH IS BEING SKIPPED
        for i in range(-min(len(result), config.max_markov_size), 0):
            # result[-min(len(result), mk)] -> result[-1]
            if result[i:] in mappings:
                if config.debug_mode:
                    print(
                        f"Taking mappings from '{result[i:]}'"
                        f" with i = {i} and result = {result}."
                    )

                selections |= mappings[result[i:]]
                selection_amount += 1

        for sequence in selections.keys():
            selections[sequence] /= selection_amount

        if config.debug_mode:
            print(f"With selections:")
            pprint(selections)

        result += pick_random_char(selections)

        if config.debug_mode and result[-1] != WORD_END:
            print(f"Now len(result) = {len(result)}.")
            print(f" > {result[-1]}")

        if result[-1] == WORD_END:
            break

    if config.debug_mode:
        print()

    return result[:-1] if result[-1] == WORD_END else result


def view_debug_details() -> None:
    print(f"Samples analysed: {samples_analysed}")
    print(f"Average size: {average_size} (min {min_size}, max {max_size})")
    print("Starting characters:")
    pprint(starting_characters)
    print("Mappings:")
    pprint(mappings)


def minimal_interpreter() -> None:
    while True:
        command = input("> ")

        if command in ["stop", "quit", "leave", "exit"]:
            break

        if command == "debug":
            view_debug_details()
        elif command == "generate":
            print(generate())
        elif command == "settings":
            config.show_settings()
        else:
            print(f"Command '{command}' not recognized.")


try:
    with open(argv[0], encoding="utf_8") as sample_file:
        for line in sample_file:
            sample_text(line)

    average_metrics()

    print(f"Input file sampled ({samples_analysed} samples analysed).")

    minimal_interpreter()
except OSError:
    print("Couldn't open file at path provided in argument 1.")
