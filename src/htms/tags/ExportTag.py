from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .TagBase import TagBase
from .constants import (
    EXPORT_TAG,
    JSON_EXPORT_FORMAT,
    CSV_EXPORT_FORMAT,
    EXCEL_EXPORT_FORMAT,
)
from htms.logging import logger
import json


@dataclass
class ExportTag:
    path: str
    format: str
    parser: str

    def __post_init__(self):
        self._tag_type = EXPORT_TAG

    @classmethod
    def from_attrs(cls, data: Dict[str, Any]) -> ExportTag:
        return ExportTag(
            path=data["path"], format=data["format"], parser=data.get("parser", None)
        )

    def export(self, data: Any):
        if self.format == JSON_EXPORT_FORMAT:
            with open(self.path, "w") as f:
                json.dump(data, f)
                logger.info(f"Exported data to '{self.path}' in JSON format")
        else:
            raise NotImplementedError(f"Export format '{self.format}' not implemented")
