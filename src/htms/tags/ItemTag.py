from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from htms.utils import remove_dup

from .TagBase import TagBase
from .RequestTag import RequestTag
from .RequestListTag import RequestListTag
from .constants import ITEM_TAG, HTML_RESPONSE_TYPE
from lxml import html

if TYPE_CHECKING:
    from htms.tags.RequestTag import RequestTag


def element_to_string(element):
    return html.tostring(element, encoding="unicode")


@dataclass
class ItemTag(TagBase):
    id: Optional[str] = None
    xpath: Optional[str] = None

    name: Optional[str] = None
    is_global: Optional[str] = None

    follow_up_url: Optional[str] = None
    follow_up_method: Optional[str] = "GET"
    follow_up_type: Optional[str] = HTML_RESPONSE_TYPE
    follow_up_parser_names: Optional[str] = None
    follow_up_concat: Optional[str] = None

    _post_parse: str = "v"
    strip: bool = False

    # the following fields are used for list operation

    # enable list
    many: Optional[bool] = False

    # list operation
    key: Optional[str] = None
    filter: Optional[str] = None
    get_items: Optional[str] = None

    value: Any = field(default=None, init=False)

    def __post_init__(self):
        self._tag_type = ITEM_TAG

    @classmethod
    def from_attrs(cls, data: Dict[str, Any]) -> ItemTag:
        return cls(
            id=data.get("id", None),
            name=data.get("name", None),
            xpath=data.get("xpath", None),
            _post_parse=data.get("parse", "value"),
            strip="strip" in data,
            many=data.get("many", False),
            key=data.get("key", None),
            filter=data.get("filter", None),
            is_global="global" in data,
            get_items=data.get("get-items", "value"),
            # follow up fields
            follow_up_url=data.get("follow-up-url", None),
            follow_up_parser_names=data.get("follow-up-parsers", "[]"),
            follow_up_method=data.get("follow-up-method", "GET"),
            follow_up_concat=data.get("follow-up-concat", None),
        )

    def get_id_or_name(self) -> str:
        return self.id or self.name

    def parse(self, value: Any, request: "RequestTag") -> Any:
        if self.xpath and isinstance(value, html.HtmlElement):
            value = value.xpath(self.xpath)

            if not self.many:
                value = value[0] if value else None

        if len(self.children) > 0:
            item_children = list(
                filter(lambda x: isinstance(x, ItemTag), self.children)
            )
            if self.many:
                value = eval(self.get_items, {}, locals())
                value = [
                    {
                        item.name: item.parse(vi, request)
                        for item in item_children
                        if item.name
                    }
                    for vi in value
                ]
            else:
                value = {
                    item.name: item.parse(value, request)
                    for item in item_children
                    if item.name
                }

        # list specific operations
        if self.many:
            if self.key:
                value = remove_dup(value, self.key)

            if self.filter:
                value = list(
                    filter(lambda x: eval(self.filter, {}, {"item": x}), value)
                )

        if self.strip and not self.many and isinstance(value, str):
            value = value.strip("\n ")
        elif self.strip and self.many:
            value = [vi.strip("\n ") if isinstance(vi, str) else vi for vi in value]

        value = eval(
            self._post_parse,
            {},
            # {
            #     "element_to_string": element_to_string,
            #     # "value": v,
            #     # "request": request,
            # },
            locals(),
        )

        self.value = value

        return value

    def has_follow_up(self) -> bool:
        return bool(self.follow_up_url and self.follow_up_parser_names)

    def generate_requests(self) -> Optional[RequestListTag]:
        if not self.has_follow_up():
            return

        if self.many:
            urls = [
                eval(self.follow_up_url, {}, {"value": value}) for value in self.value
            ]
        else:
            urls = [eval(self.follow_up_url, {}, {"value": self.value})]
        rl = RequestListTag.from_attrs(
            {
                "parsers": self.follow_up_parser_names,
                "concat": self.follow_up_concat,
                "method": self.follow_up_method,
                "type": self.follow_up_type,
                "meta": self.value,
            }
        )
        rl._list = urls
        return rl
