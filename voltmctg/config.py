from dataclasses import dataclass


@dataclass
class Config:
    enable_warnings: bool = True
    case_sensitive: bool = False
    debug_mode: bool = False
    max_markov_size: int = 4

    def show_settings(self) -> None:
        print("Current settings:")
        print(f"    Warnings enabled: {self.enable_warnings}")
        print(f"    Case sensitive: {self.case_sensitive}")
        print(f"    Debug mode: {self.debug_mode}")
        print(f"    Max Markov size: {self.max_markov_size}")
