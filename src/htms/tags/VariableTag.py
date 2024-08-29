from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .TagBase import TagBase
from .constants import VARIABLE_TAG
from htms.logging import logger
import json
import requests
import http


@dataclass
class VariableTag(TagBase):
    name: str = field(default=None)
    value: str = field(default=None)
    value_type: str = field(default="str")

    def __post_init__(self):
        self._tag_type = VARIABLE_TAG

    @classmethod
    def from_attrs(cls, data: Dict[str, Any]) -> VariableTag:
        return VariableTag(
            name=data["name"],
            value=data["value"],
            value_type=data.get("value_type", "str"),
        )

    def get_value(self) -> Any:
        if self.value_type == "str":
            return self.value
        elif self.value_type == "int":
            return int(self.value)
        elif self.value_type == "float":
            return float(self.value)
        elif self.value_type == "bool":
            return self.value.lower() == "true"
        elif self.value_type == "dict":
            return json.loads(self.value)
        elif self.value_type == "list":
            return json.loads(self.value)
        else:
            return self.value
