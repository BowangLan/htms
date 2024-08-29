from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING

from htms.tags.ExportTag import ExportTag

from .TagBase import TagBase
from .constants import REQUEST_TAG, JSON_RESPONSE_TYPE, HTML_RESPONSE_TYPE

if TYPE_CHECKING:
    from htms.tags.ListTag import ListTag, ItemTag


@dataclass
class RequestTagBase:
    url: str
    parser_names: List[str]
    method: str = "GET"
    headers: Optional[Dict[str, str]] = field(default_factory=dict)
    meta: Optional[Dict[str, Any]] = field(default_factory=dict)

    response_type: Optional[str] = HTML_RESPONSE_TYPE

    parsers: List[Union[ItemTag, ListTag]] = field(default_factory=list, init=False)


@dataclass
class RequestTag(TagBase, RequestTagBase):

    def __post_init__(self):
        self._tag_type = REQUEST_TAG

    @staticmethod
    def from_attrs(data: Dict[str, Any]) -> RequestTag:
        parser_names = (
            [x.strip() for x in data["parsers"].split(",")] if "parsers" in data else []
        )
        return RequestTag(
            url=data["url"],
            parser_names=parser_names,
            method=data.get("method", "GET"),
            headers=data.get("headers", {}),
            response_type=data.get("type", HTML_RESPONSE_TYPE),
        )

    def __str__(self) -> str:
        pnames = list(map(lambda x: x.get_id_or_name(), self.parsers))
        return f"<RequestTag url='{self.url}' parser_names={self.parser_names} parsers={pnames} >"

    def __repr__(self) -> str:
        pnames = list(map(lambda x: x.get_id_or_name(), self.parsers))
        return f"<RequestTag url='{self.url}' parser_names={self.parser_names} parsers={pnames} >"

    def get_export_tags(self) -> List[ExportTag]:
        return list(filter(lambda x: isinstance(x, ExportTag), self.children))
