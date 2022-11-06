from dataclasses import dataclass


@dataclass
class Config:
    enable_warnings: bool = True
    case_sensitive: bool = False
