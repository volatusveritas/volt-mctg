from pprint import pprint
from sys import argv, exit
import random
from typing import TypeAlias


# Remove script name from args
del argv[0]


if not len(argv):
    print("Not enough arguments, please provide argument 1 (file path).")
    exit()


ChanceTable: TypeAlias = dict[str, float]
FollowingTable: TypeAlias = dict[str, ChanceTable]


WORD_END: str = "\0"


samples_analysed: int = 0

appearances: dict[str, int] = {}
mappings: FollowingTable = {}
starting_characters: ChanceTable = {}

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
    char = char.lower()

    if not char in starting_characters:
        starting_characters[char] = 0.0

    starting_characters[char] += 1.0


def consider_segment(base: str, sequence: str) -> None:
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

    consider_size(sample_size)
    consider_starting_character(sample[0])

    for segment_size in range(2, sample_size):
        for i in range(sample_size - 1):
            consider_segment(sample[i], sample[i + 1])

    samples_analysed += 1


def pick_random_char(choice_map: dict[str, float]) -> str:
    threshold: float = random.random()

    for char in choice_map.keys():
        if choice_map[char] >= threshold:
            return char

        threshold -= choice_map[char]

    # NOTE: This value is never returned, this statement is for static checkers
    return ""


def generate() -> str:
    result: str = pick_random_char(starting_characters)

    while len(result) < max_size:
        result += pick_random_char(mappings[result[-1]])

        if result[-1] == WORD_END:
            break

    return result


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


try:
    with open(argv[0], encoding="utf_8") as sample_file:
        for line in sample_file:
            sample_text(line)

    average_metrics()

    print(f"Input file sampled ({samples_analysed} samples analysed).")

    minimal_interpreter()
except OSError:
    print("Couldn't open file at path provided in argument 1.")
