from html.parser import HTMLParser
from lxml import html
from rich import print
import requests
import json
from pathlib import Path
from htms.constants import DEFAULT_HEADERS
from typing import List, Dict, Optional, Any, Union
from htms.tags.RequestListTag import RequestListTag
from htms.tags.ItemTag import ItemTag
from htms.tags.ListTag import ListTag
from htms.tags.RequestTag import RequestTag
from htms.tags.ExportTag import ExportTag
from htms.logging import logger
from htms.tags.constants import (
    ITEM_TAG,
    LIST_TAG,
    REQUEST_LIST_TAG,
    REQUEST_TAG,
    HTML_RESPONSE_TYPE,
    JSON_RESPONSE_TYPE,
)

"""
Notes

* Scrape a table, or a list of dictionaries;
* Scrape an item using xpath;
* Scrape an item with extra custom parsing;
* Nested scraping: follow-up requests and scrapings
* Output the scraped data to a JSON file
* Request list, or for loop to scrape multiple pages


*** These are in very early stages so they're very ugly. ***
"""

DISPLAY_SAMPLE_DATA_COUNT = 3

TagMap = {
    REQUEST_TAG: RequestTag,
    LIST_TAG: ListTag,
    ITEM_TAG: ItemTag,
    "export": ExportTag,
    REQUEST_LIST_TAG: RequestListTag,
}


class HTMSParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.requests: List[RequestTag] = []
        self.request_generators: List[RequestListTag] = []
        self.global_parsers: Dict[str, ItemTag] = {}
        self.exports = []
        self.items: List[ItemTag] = []
        self.parents: List[ItemTag] = []

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        attrs_dict = dict(attrs)

        if tag not in TagMap:
            raise ValueError(f"Invalid tag: {tag}")

        if "parent" in attrs_dict:
            raise ValueError("Attribute named 'parent' is not allowed")

        if "children" in attrs_dict:
            raise ValueError("Attribute named 'children' is not allowed")

        tag_ins = TagMap[tag].from_attrs(attrs_dict)

        if len(self.parents) > 0:
            tag_ins.parent = self.parents[-1]
            self.parents[-1].children.append(tag_ins)

        if tag_ins._tag_type == REQUEST_TAG:
            self.requests.append(tag_ins)

        if isinstance(tag_ins, ItemTag) and tag_ins.id:
            # print("Global item detected")
            if not tag_ins.id:
                raise ValueError("Global item must have an id")
            self.global_parsers[tag_ins.id] = tag_ins

        if isinstance(tag_ins, RequestListTag):
            self.request_generators.append(tag_ins)

        self.parents.append(tag_ins)

    def handle_endtag(self, tag):
        t = self.parents.pop()

    def handle_data(self, data):
        pass

    def feed(self, data: str) -> None:
        res = super().feed(data)

        return res

    def _fetch_page(
        self, url: str, method: str, headers: Dict[str, str]
    ) -> Optional[requests.Response]:
        try:
            response = requests.request(method, url, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None

    def _fill_request_with_parser_objs(
        self, req: Union[RequestTag, RequestListTag]
    ) -> List[ItemTag]:
        parsers = list(
            filter(
                lambda x: isinstance(x, ItemTag) or isinstance(x, ListTag),
                req.children,
            )
        )
        for pn in req.parser_names:
            if pn not in self.global_parsers:
                logger.error(f"Parser '{pn}' not found")
                continue
            p = self.global_parsers[pn]
            parsers.append(p)
        req.parsers = parsers

    def start_request(self, req: RequestTag):
        self._fill_request_with_parser_objs(req)

        logger.info(f"Starting request: {req}")
        url = req.url
        method = req.method
        request_params = {
            "headers": {**DEFAULT_HEADERS, **req.headers},
            # "params": req.get("params", {}),
            # "data": req.get("data", {}),
            # "json": req.get("json", {}),
        }

        logger.debug(f"Request: {req}")
        logger.info(f"[{method}] '{url}'")

        # Fetch the web page
        response = self._fetch_page(url, method, request_params["headers"])

        # with open("output.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        response_value = response.text

        if req.response_type == HTML_RESPONSE_TYPE:
            try:
                tree = html.fromstring(response.content)
            except Exception as e:
                logger.error(f"Failed to parse document:", e)
                return
        elif req.response_type == JSON_RESPONSE_TYPE:
            try:
                tree = json.loads(response_value)
            except Exception as e:
                logger.error(f"Failed to parse JSON:", e)
                return
        else:
            logger.error(f"Invalid response type: {req.response_type}")
            return

        req_output = {p.get_id_or_name(): [] for p in req.parsers}
        logger.info(f"Request output template: {req_output}")

        for p in req.parsers:
            name = p.get_id_or_name()
            if p.many:
                req_output[name] += p.parse(tree, req)
            else:
                req_output[name] = p.parse(tree, req)

            if p.has_follow_up():
                follow_up_req_list = p.generate_requests()
                self.request_generators.append(follow_up_req_list)
                logger.info(
                    f"Generated {len(follow_up_req_list._list)} follow-up requests"
                )

        output_stats = {k: len(v) for k, v in req_output.items()}
        logger.info(f"Output stats: {output_stats}")
        for k, v in req_output.items():
            print(f"{k}:")
            if isinstance(v, list):
                for i in range(
                    DISPLAY_SAMPLE_DATA_COUNT
                    if len(v) > DISPLAY_SAMPLE_DATA_COUNT
                    else len(v)
                ):
                    print(v[i])
                if len(v) > DISPLAY_SAMPLE_DATA_COUNT:
                    print(f"... and {len(v) - DISPLAY_SAMPLE_DATA_COUNT} more")
            else:
                print(v)
        # print(req_output)

        return req_output

    def start_request_list(self, request_list: RequestListTag):
        self._fill_request_with_parser_objs(request_list)

        logger.info(f"Starting request list: {request_list}")

        requests = request_list.generate_requests()
        logger.info(f"Generated {len(requests)} requests")

        output = {p.get_id_or_name(): [] for p in request_list.parsers}
        logger.info(f"Output template: {output}")

        for req in requests:
            req_output = self.start_request(req)
            for k, v in req_output.items():
                if k in request_list.concat:
                    output[k] += v
                else:
                    output[k].append(v)

        output_stats = {k: len(v) for k, v in output.items()}
        logger.info(f"Output stats: {output_stats}")

        # print the first 5 items for each key
        for k, v in output.items():
            print(f"{k}:")
            if isinstance(v, list):
                for i in range(
                    DISPLAY_SAMPLE_DATA_COUNT
                    if len(v) > DISPLAY_SAMPLE_DATA_COUNT
                    else len(v)
                ):
                    print(v[i])
                if len(v) > DISPLAY_SAMPLE_DATA_COUNT:
                    print(f"... and {len(v) - DISPLAY_SAMPLE_DATA_COUNT} more")
            else:
                print(v)

        return output

    def start(self):
        if len(self.requests) == 0 and len(self.request_generators) == 0:
            return

        logger.info("Starting the scraping process")

        self.output = []

        while len(self.requests) > 0 or len(self.request_generators) > 0:
            logger.info(f"While loop: {len(self.requests)} requests left")

            export_tags = []

            if len(self.requests) > 0:
                req = self.requests.pop(0)
                output = self.start_request(req)
                export_tags = req.get_export_tags()
            else:
                req_gen = self.request_generators.pop(0)
                output = self.start_request_list(req_gen)
                export_tags = req_gen.get_export_tags()

            for export_tag in export_tags:
                export_tag.export(output)

            # print(req)

            # pagination
            # if the pagination-xpath is provided, then we will get the total pages
            # and create a new request for each page
            # assumes that the pagination-xpath returns a number
            # and the url-template is not none and a python expression
            # if req.get("pagination-xpath"):
            #     print("Pagination detected")
            #     total_page_el = tree.xpath(req["pagination-xpath"])
            #     if len(total_page_el) > 0:
            #         try:
            #             total_pages = int(total_page_el[0])
            #             for i in range(req["start"], total_pages + 1):
            #                 next_url = eval(req["url-template"], {}, {"i": i})
            #                 self.requests.append(
            #                     {
            #                         "method": req["method"],
            #                         "url": next_url,
            #                         "parser": req["parser"],
            #                     }
            #                 )
            #             print(
            #                 f"Added {total_pages - req['start'] + 1} pages to the request queue"
            #             )
            #         except Exception as e:
            #             print(f"Failed to parse total pages:", e)

        self.output.append(output)

        # print("Scraped Data:", self.output)

        # res_stats = {k: len(v) for k, v in self.output.items()}
        # print("Scraped Data Stats:", res_stats)
