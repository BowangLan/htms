from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

from htms.tags.ExportTag import ExportTag
from htms.tags.TagBase import TagBase
from htms.tags.RequestTag import RequestTag
from htms.tags.constants import REQUEST_LIST_TAG, JSON_RESPONSE_TYPE, HTML_RESPONSE_TYPE


@dataclass
class RequestListTagBase:
    _list: List[Any] = field(default_factory=list)
    get_url: str = ""
    # pagination_xpath: Optional[str] = None

    method: str = "GET"
    headers: Optional[Dict[str, str]] = field(default_factory=dict)
    meta: Optional[Dict[str, Any]] = field(default_factory=dict)

    parser_names: List[str] = field(default_factory=list)

    # will be filled by HTMSParser
    parsers: List[Union[RequestTag, RequestListTag]] = field(
        default_factory=list, init=False
    )

    # list of parser ids or names to concat the results
    # parser output must be a list
    concat: List[str] = field(default_factory=list)

    response_type: Optional[str] = None


@dataclass
class RequestListTag(TagBase, RequestListTagBase):

    def __post_init__(self):
        self._tag_type = REQUEST_LIST_TAG

    @classmethod
    def from_attrs(cls, data: Dict[str, Any]) -> RequestListTag:
        parser_names = (
            [x.strip() for x in data["parsers"].split(",")] if "parsers" in data else []
        )
        concat = (
            [x.strip() for x in data["concat"].split(",")] if data.get("concat") else []
        )
        return cls(
            _list=eval(data.get("list", "[]"), {}, locals()),
            get_url=data.get("get-url", "lambda x: x"),
            parser_names=parser_names,
            method=data.get("method", "GET"),
            headers=data.get("headers", {}),
            concat=concat,
            response_type=data.get("type", HTML_RESPONSE_TYPE),
            meta=data.get("meta", {}),
        )

    def generate_requests(self) -> List[RequestTag]:
        requests = []
        for item in self._list:
            url = eval(self.get_url, {}, locals())(item)
            print(self.parser_names)
            r = RequestTag(
                url=url,
                parser_names=self.parser_names,
                method=self.method,
                headers=self.headers,
                meta=self.meta,
                response_type=self.response_type,
                children=self.children,
            )
            requests.append(r)
        return requests

    def __str__(self) -> str:
        return f'<RequestListTag list={self._list} get_url="{self.get_url}" method="{self.method}" parser_names={self.parser_names} concat={self.concat}>'

    def __repr__(self) -> str:
        return f'<RequestListTag list={self._list} get_url="{self.get_url}" method="{self.method}" parser_names={self.parser_names} concat={self.concat}>'

    def get_export_tags(self) -> List[ExportTag]:
        return list(filter(lambda x: isinstance(x, ExportTag), self.children))
