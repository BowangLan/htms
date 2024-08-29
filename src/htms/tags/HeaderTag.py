from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .TagBase import TagBase
from .constants import EXPORT_TAG, HEADER_TAG
from htms.logging import logger
import json


@dataclass
class HeaderTag(TagBase):

    def __post_init__(self):
        self._tag_type = HEADER_TAG

    @classmethod
    def from_attrs(cls, data: Dict[str, Any]) -> HeaderTag:
        return HeaderTag(**data)
