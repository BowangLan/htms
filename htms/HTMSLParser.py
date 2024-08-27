from html.parser import HTMLParser
from lxml import html
from rich import print
import requests
import json
from pathlib import Path
from htms.constants import DEFAULT_HEADERS


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


def remove_dup(items: list[dict], key: str):
    keys = set()
    output = []
    for item in items:
        v = item[key]
        if v in keys:
            continue
        keys.add(v)
        output.append(item)
    return output


def parse_lambda(lambda_str: str, value: any, default_str: str):
    try:
        parse_function = eval(lambda_str)
        if callable(parse_function):
            parsed_value = parse_function(value)
            return parsed_value
        else:
            print(f"Invalid parse function: {lambda_str}")
            return default_str
    except Exception as e:
        print(f"Failed to parse with error: {e}")
        return default_str


class HTMSParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.requests = []
        self.list_scrapers = {}
        self.field_scrapers = []
        self.outputs = []
        self.items = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        if tag == 'request':
            method = attrs_dict.get('method', 'GET')
            self.requests.append({
                'url': attrs_dict.get('url'),
                'parser': attrs_dict.get('parser'),
                'method': method,
            })
        elif tag == 'request-list':
            start_i = int(attrs_dict.get('start', 1))
            end_i = attrs_dict.get('end')
            pagination_xpath = attrs_dict.get('pagination-xpath')

            if end_i:
                end_i = int(end_i)

                for i in range(start_i, end_i + 1):
                    url = eval(
                        attrs_dict.get('url-template'),
                        {},
                        {"i": i}
                    )
                    parser = attrs_dict.get('parser')
                    method = attrs_dict.get('method', 'GET')
                    req = {
                        'url': url,
                        'parser': parser,
                        'method': method,
                    }
                    self.requests.append(req)
            else:
                first_url = eval(
                    attrs_dict.get('url-template'),
                    {},
                    {"i": start_i}
                )
                req = {
                    'url': first_url,
                    'url-template': attrs_dict.get('url-template'),
                    'parser': attrs_dict.get('parser'),
                    'method': attrs_dict.get('method', 'GET'),
                    'start': start_i + 1,
                    'pagination-xpath': pagination_xpath,
                }
                self.requests.append(req)
        elif tag == 'list':
            name = attrs_dict.get('name')
            self.list_scrapers[name] = {
                **attrs_dict,
                'items': [],
            }
            self.current = self.list_scrapers[name]
        elif tag == 'item':
            strip = False
            if 'strip' in attrs_dict:
                strip = True

            self.current['items'].append({
                **attrs_dict,
                "strip": strip,
            })
        elif tag == 'field':
            self.field_scrapers.append(attrs_dict)
        elif tag == 'output':
            self.outputs.append(attrs_dict)

    def handle_endtag(self, tag):
        if tag == 'list':
            pass
        elif tag == 'item':
            pass
        elif tag == "request":
            pass

    def handle_data(self, data):
        pass

    def start(self):
        if len(self.requests) == 0:
            return

        res = {}

        while len(self.requests) > 0:
            req = self.requests.pop(0)

            url = req.get("url")
            method = req.get("method", "GET")
            request_params = {
                "headers": {**DEFAULT_HEADERS, **req.get("headers", {})},
                # "params": req.get("params", {}),
                # "data": req.get("data", {}),
                # "json": req.get("json", {}),
            }

            # print(req)

            print(f"[{method}] '{url}'")

            # Fetch the web page
            response = requests.request(method, url, **request_params)

            # with open("output.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)

            try:
                tree = html.fromstring(response.content)
            except Exception as e:
                print(f"Failed to parse document:", e)
                continue

            parser_names = [x.strip("") for x in req['parser'].split(",")]
            parsers = [self.list_scrapers[n] for n in parser_names]

            for parser in parsers:
                p_name = parser['name']
                list_elements = tree.xpath(parser['xpath'])
                list_data = []
                for item_element in list_elements:
                    item_data = {}
                    for item_scraper in parser['items']:
                        v = item_element

                        if item_scraper.get("xpath"):
                            v = item_element.xpath(item_scraper['xpath'])

                            if v:
                                v = v[0]

                        if item_scraper.get('parse'):
                            v = eval(item_scraper['parse'], {}, {
                                "value": v,
                                "parser": parser,
                                "request": req,
                            })

                        if item_scraper.get('strip') and isinstance(v, str):
                            v = v.strip("\n ")

                        item_data[item_scraper['name']] = v

                    list_data.append(item_data)

                # deal with extra list tag attributes

                if parser.get('parse-items'):
                    list_data = parse_lambda(
                        parser['parse-items'],
                        list_data,
                        list_data)

                if parser.get('filter'):
                    list_data = list(
                        filter(lambda x: eval(parser['filter'], {}, {'item': x}), list_data))

                if parser.get('key'):
                    list_data = remove_dup(list_data, parser['key'])

                if p_name not in res:
                    res[p_name] = list_data
                else:
                    res[p_name] = res[p_name] + list_data

                # follow-up requests configuration
                if parser.get("follow-up-parser"):
                    method = parser.get("method")
                    for item in list_data:
                        self.requests.append({
                            "method": "GET" if not method else method,
                            "url": eval(
                                parser['url-template'],
                                {},
                                {"item": item}
                            ),
                            "parser": parser["follow-up-parser"],
                            "meta": item,
                        })

            # deal with request-level options

            # print(req)

            # pagination
            # if the pagination-xpath is provided, then we will get the total pages
            # and create a new request for each page
            # assumes that the pagination-xpath returns a number
            # and the url-template is not none and a python expression
            if req.get("pagination-xpath"):
                print("Pagination detected")
                total_page_el = tree.xpath(req['pagination-xpath'])
                if len(total_page_el) > 0:
                    try:
                        total_pages = int(total_page_el[0])
                        for i in range(req['start'], total_pages + 1):
                            next_url = eval(
                                req['url-template'],
                                {},
                                {"i": i}
                            )
                            self.requests.append({
                                "method": req['method'],
                                "url": next_url,
                                "parser": req['parser'],
                            })
                        print(
                            f"Added {total_pages - req['start'] + 1} pages to the request queue")
                    except Exception as e:
                        print(f"Failed to parse total pages:", e)

        print("Scraped Data:", res)
        res_stats = {k: len(v) for k, v in res.items()}
        print("Scraped Data Stats:", res_stats)

        # output the data
        for output in self.outputs:
            if output.get("type") == "json":
                parser_name = output['parser']
                if parser_name not in res:
                    print(
                        f"Invalid parser name from output config: {parser_name}")
                    continue
                data = res[parser_name]
                path = output['path']
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                    print(f"Saved {len(data)} items to '{path}'")
