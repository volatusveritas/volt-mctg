from sys import argv, exit


if not len(argv):
    print("Not enough arguments, please provide argument 1 -- file path.")
    exit()


samples_analysed: int = 0

appearances: dict[str, int] = {}
mappings: dict[str, dict[str, float]] = {}
starting_characters: dict[str, float] = {}

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
    if not char in starting_characters:
        starting_characters[char] = 0.0

    starting_characters[char] += 1.0


# NOTE: This uses a one-segment Markov chain
def consider_character(base: str, char: str) -> None:
    # TODO: Add option to make this case sensitive
    base = base.lower()
    char = char.lower()

    if not base in mappings:
        appearances[base] = 0
        mappings[base] = {}

    if not char in mappings[base]:
        mappings[base][char] = 0.0

    appearances[base] += 1
    mappings[base][char] += 1.0


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

    sample_size: int = len(sample)

    consider_size(sample_size)
    consider_starting_character(sample[0])

    for i in range(sample_size - 1):
        consider_character(sample[i], sample[i + 1])

    samples_analysed += 1


try:
    with open(argv[0]) as sample_file:
        for line in sample_file:
            sample_text(line)

        average_metrics()

        print("Input file sampled.")
except OSError:
    print("Couldn't open file at path provided in argument 1.")
