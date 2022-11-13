from dataclasses import dataclass


@dataclass
class Config:
    enable_warnings: bool = False
    case_sensitive: bool = False
    debug_mode: bool = False
    max_markov_size: int = 4

    def from_args(self, args) -> None:
        self.enable_warnings = args.warnings
        self.case_sensitive = args.case_sensitive
        self.debug_mode = args.debug

        if args.max_markov_size:
            self.max_markov_size = args.max_markov_size

    def show_settings(self) -> None:
        print("Current settings:")
        print(f"    enable_warnings is {self.enable_warnings}")
        print(f"    case_sensitive is {self.case_sensitive}")
        print(f"    debug_mode is {self.debug_mode}")
        print(f"    max_markov_size is {self.max_markov_size}")
