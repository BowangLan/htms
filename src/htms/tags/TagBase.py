from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class TagBase:
    _tag_type: str = field(init=False)
    children: List[TagBase] = field(default_factory=list)
    parent: Optional[TagBase] = None

    @staticmethod
    def from_attrs(data: Dict[str, Any]) -> TagBase:
        raise NotImplementedError(
            "from_attrs method must be implemented in child class"
        )
