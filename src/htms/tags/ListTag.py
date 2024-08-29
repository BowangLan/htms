from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .ItemTag import ItemTag
from .constants import LIST_TAG
from lxml import html


@dataclass
class ListTag(ItemTag):

    def __post_init__(self):
        self._tag_type = LIST_TAG
        self.many = True
