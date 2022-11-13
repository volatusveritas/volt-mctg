from pprint import pprint
from typing import Optional, TypeAlias
import random

from voltmctg.config import Config


ChoiceMap: TypeAlias = dict[str, float]
FollowingTable: TypeAlias = dict[str, ChoiceMap]


WORD_END: str = "\0"


class MarkovChainTextGenerator:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config: Config = config if config else Config()

        self.samples_analysed: int
        self.appearances: dict[str, int]
        self.mappings: FollowingTable
        self.starting_characters: ChoiceMap
        self.min_size: int
        self.max_size: int
        self.average_size: float

        self.reset_state()

    def reset_state(self) -> None:
        self.samples_analysed = 0
        self.appearances = {}
        self.mappings = {}
        self.starting_characters = {}
        self.min_size = -1
        self.max_size = -1
        self.average_size = 0.0

    def consider_size(self, size: int) -> None:
        if self.min_size == -1 or size < self.min_size:
            self.min_size = size

        if self.max_size == -1 or size > self.max_size:
            self.max_size = size

        self.average_size += size

    def consider_starting_character(self, char: str) -> None:
        if not self.config.case_sensitive:
            char = char.lower()

        if not char in self.starting_characters:
            self.starting_characters[char] = 0.0

        self.starting_characters[char] += 1.0

    def consider_segment(self, base: str, sequence: str) -> None:
        if not self.config.case_sensitive:
            base = base.lower()
            sequence = sequence.lower()

        if not base in self.mappings:
            self.appearances[base] = 0
            self.mappings[base] = {}

        if not sequence in self.mappings[base]:
            self.mappings[base][sequence] = 0.0

        self.appearances[base] += 1
        self.mappings[base][sequence] += 1.0

    def average_sizes(self) -> None:
        self.average_size /= self.samples_analysed

    def average_starting_characters(self) -> None:
        for char in self.starting_characters.keys():
            self.starting_characters[char] /= self.samples_analysed

    def average_mappings(self) -> None:
        for base in self.mappings.keys():
            for char in self.mappings[base].keys():
                self.mappings[base][char] /= self.appearances[base]

    def average_metrics(self) -> None:
        self.average_sizes()
        self.average_starting_characters()
        self.average_mappings()

    def sample_text(self, sample: str) -> None:
        sample = sample[:-1] + WORD_END

        sample_size: int = len(sample)

        if sample_size < 2:
            if self.config.enable_warnings:
                print(
                    f"[Warning] Invalid sample size found for '{sample}'."
                    " Skipping."
                )

            return

        self.consider_size(sample_size)
        self.consider_starting_character(sample[0])

        for segment_size in range(1, (
            sample_size if self.config.max_markov_size == -1
            else min(self.config.max_markov_size + 1, sample_size)
        )):
            for i in range(sample_size - segment_size):
                self.consider_segment(
                    sample[i : i + segment_size],
                    sample[i + segment_size]
                )

        self.samples_analysed += 1

    def sample_texts(
        self,
        samples: list[str],
        reset: bool = False,
        average: bool = False
    ) -> None:
        if reset:
            self.reset_state()

        for sample in samples:
            self.sample_text(sample)

        if average:
            self.average_metrics()

    def sample_file(
        self,
        path: str,
        reset: bool = True,
        average: bool = True
    ) -> None:
        if reset:
            self.reset_state()

        with open(path, encoding="utf_8") as samples_file:
            for line in samples_file:
                self.sample_text(line)

        if average:
            self.average_metrics()

    def pick_random_char(self, choice_map: ChoiceMap) -> str:
        threshold: float = random.random()

        for char in choice_map.keys():
            if choice_map[char] >= threshold:
                return char

            threshold -= choice_map[char]

        # NOTE: This value is never returned, this statement is for static checkers
        return ""

    def generate(self) -> str:
        result: str = ""

        while len(result) < self.min_size:
            result: str = self.pick_random_char(self.starting_characters)

            if self.config.debug_mode:
                print("Generation steps:")
                print(result)

            while len(result) < self.max_size:
                selection_amount: int = 0
                selections: ChoiceMap = {}

                for i in range(
                    -min(len(result), self.config.max_markov_size), 0
                ):
                    if result[i:] in self.mappings:
                        if self.config.debug_mode:
                            print(
                                f"Taking mappings from '{result[i:]}'"
                                f" with i = {i} and result = {result}."
                            )

                        selections |= self.mappings[result[i:]]
                        selection_amount += 1

                for sequence in selections.keys():
                    selections[sequence] /= selection_amount

                if self.config.debug_mode:
                    print(f"With selections:")
                    pprint(selections)

                result += self.pick_random_char(selections)

                if self.config.debug_mode and result[-1] != WORD_END:
                    print(f"Now len(result) = {len(result)}.")
                    print(f" > {result[-1]}")

                if result[-1] == WORD_END:
                    break

            if self.config.debug_mode:
                print()

        return result[:-1] if result[-1] == WORD_END else result
