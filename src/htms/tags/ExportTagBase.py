from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .TagBase import TagBase
from .constants import EXPORT_TAG


@dataclass
class ExportTagBase(TagBase):
    path: str
    export_type: str
    parser: str

    def __post_init__(self):
        self._tag_type = EXPORT_TAG

    def export(self, data: Any) -> None:
        raise NotImplementedError(
            "ExportTagBase.export() must be implemented in subclasses"
        )
