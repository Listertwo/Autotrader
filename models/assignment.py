from dataclasses import dataclass, field
from strategies.base import Strategy

@dataclass
class Assignment:
	strategy: Strategy
	symbols: list[str] = field(default_factory=list)
