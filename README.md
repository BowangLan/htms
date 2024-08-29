# HTMS: HTML-based Web Scraping Library

## Overview

HTMSLParser is a Python library for web scraping using an HTML-like configuration. It simplifies data extraction, handles pagination, and supports custom parsing, making it easy to gather structured data from websites with minimal coding.

## Features

- **Declarative Scraping Configuration:** Define scraping tasks using an HTML-like syntax to specify requests, lists, items, and outputs.
- **Supports XPath Data Extraction**
- **Pagination Handling:** Automatically manage pagination by defining start, end, and URL templates.
- **Follow-up Requests:** Enable follow-up scraping on specific items based on extracted data from initial requests.
- **Multiple Parsers:** Combine and use multiple parsers for complex scraping tasks.
- **Flexible Data Extraction:** Use XPath for precise data extraction, including support for custom parsing and filtering.
- **JSON Output:** Export scraped data directly to JSON files.
- **Item Data Manipulation:** Strip whitespace, parse data, and apply filters to extracted items.
- **Request Configuration:** Supports GET and POST methods with customizable headers.

## Installation


You can install the package using `pip` if it is available on PyPI:

```bash
pip install htms
```

Alternatively, to install htms, simply clone the repository and include it in your project:

```bash
git clone https://github.com/BowangLan/htms.git
```

## Getting Started

htms lets you specify common web scraping tasks in HTML. To run an htms HTML file therefore is to run web scraping tasks described inside the HTML file.

Command for running an htms HTML file:

```
python -m htms <your-html-file>
```

Alternatively, you can use call the Python API to run the HTML file:

```python
from htms import HTMSParser

with open('your-html-file.html', 'r') as file:
    html_str = file.read()

parser = HTMSParser()
parser.feed(html_str)
parser.start()
```

## Run Examples

A list of example HTML files are included in this repo under `src/htms/example_html` folder. To run these, use this command:

```
python -m htms.examples <example-file-name>
```

You can see a full list of example files using this command:

```
python -m htms.examples
```

## HTML Configuration

### Basic Example

Suppose you want to scrape badminton club locations from `badmintonclubs.org`. The following configuration will extract the name and href of each club listed on the site:

```html
<request url="https://badmintonclubs.org">
  <list xpath="//map/area" name="locations" key="href">
    <item
      name="name"
      xpath="@title"
      parse="value.split('badminton in ')[1] if value else None"
    ></item>
    <item name="href" xpath="@href"></item>
  </list>
</request>
```

You make a request by a `RequestTag` . Then, you create a `ListTag` inside this request tag for parsing the output of this request. Then, for each location element extract by `xpath` in the `ListTag` , you extract two fields (name and value) by nesting two `ItemTag` inside the `ListTag` .

- `key` attribute in the list tag tells the parser to remove duplicates of the extracted object list by the provided key. In the above case, locations that has the same href are dropped.

This HTML snippet is equivalent to the followinig Python code:

```python
import requests
from lxml import html

output = []

url = "https://badmintonclubs.org"
response = requests.get(url)

tree = html.fromstring(response.content)

locations = tree.xpath("//map/area")

result = []
for location in locations:
    name = location.xpath("@title")[0] if location.xpath("@title") else None
    href = location.xpath("@href")[0] if location.xpath("@href") else None
    
    # Parse the name field according to the provided logic
    if name:
        name = name.split('badminton in ')[1] if 'badminton in ' in name else None
    
    result.append({
        "name": name,
        "href": href
    })

href_set = set()
new_result = []
for item in result:
    if item['href'] in href_set:
        continue
    href_set.add(item['href'])
    new_result.append(iem)
result = new_result

output.append({
  "locations": result
})
```

### `ListTag` and `ItemTag`
<!-- 
- `name`: This is used to specify the key in the parent tag (can be an `ItemTag` , `ListTag` , or `RequestTag` )
- `id` (optional)
- `xpath`: XPath using which the input value is being parsed.

`ListTag` specific 
- `key` : remove duplicates;
- `filter`: filter 

- `parse`: custom parsing -->

`ItemTag` and `ListTag` are abstractions designed to simplify the process of extracting and processing data from HTML responses in a structured and intuitive manner. These abstractions allow you to define the extraction logic using a declarative syntax, making it easy to manage complex scraping tasks.

#### `ItemTag`

The ItemTag represents a single data extraction operation. It is used to extract a single value from a given HTML element based on the specified XPath.

Attributes for both `ItemTag` and `ListTag` :

- `name`: The name of the field being extracted.
- `id` (optional): An optional global id of the parser.
- `xpath`: The XPath expression used to locate the data within the HTML element.
- `parse` (optional): An optional inline Python expression runs after all other processing steps and right before returning the extracted value.
- `pre-parse` (optional): An optional inline Python expression that runs before passing the value to child parsers.

Attributes specific to `ItemTag` :

- `strip`: Strip whitespace and `\n` from string values.

Example Usage:

```html
<item name="title" xpath="//h1/text()" parse="value.strip()"></item>
```

This example extracts the text content of an `<h1>` element, and then applies a strip() operation to remove any leading or trailing whitespace.

`ListTag`

The `ListTag` is an extension of `ItemTag` that handles the extraction of multiple values from a list of HTML elements. It is useful when you need to process a collection of similar elements, such as a list of articles or links.

Attributes specific to `ListTag` :

- All attributes of `ItemTag`.
- `key` (optional): The field by which to remove duplicates from the list.
- `filter` (optional)

Example Usage:

```html
<list xpath="//div[@class='articles']/article" name="articles" key="url">
  <item name="title" xpath=".//h2/text()" />
  <item name="url" xpath=".//a/@href" />
</list>
```

This example extracts a list of articles from a page. Each article has a title and a url, and duplicates are removed based on the url field.

### `RequestTag`

The `RequestTag` represents a single HTTP request and the associated data extraction process. 

The response of the request is parsed based on the `type` attribute, which specifies the type of response. 

The child tags of a `RequestTag` can be: 

- `ItemTag` or `ListTag` for data extraction.
- `ExportTag` for exporting data.
- ... (TODO)

Attributes:

- `url`: URL of the request.
- `parsers` (optional): An optional string field for specifying external parsers ( `ListTag` or `ItemTag` ) by id separated by `,` . 
- `type` (optional): Specifies the type of response. Either `"json"` or `"html"`. Default to `"html"` .
- `method` (optional)

<!-- 
### `ExportTag`

Attributes

- `path` -->

<!-- ### Handling Pagination

HTMSParser supports pagination by defining a `request-list` in the HTML configuration. For example, to scrape multiple pages of news articles from a website:

#### HTML Configuration

```html
<request-list
  start="1"
  end="5"
  url-template="'https://phys.org/space-news/astronomy/page' + str(i) + '.html'"
  parser="main-news"
></request-list>
<list name="main-news" xpath="//article[@class='sorted-article']" key="url">
  <item name="url" xpath=".//a/@href"></item>
  <item name="title" xpath=".//h3/a/text()"></item>
  <item name="subtitle" xpath=".//p/text()" strip></item>
  <item name="date" xpath="./div[2]/div[2]/p/text()" strip></item>
  <item
    name="view_count"
    xpath="./div[2]/div[4]/p/span/text()"
    strip
    parse="int(value)"
  ></item>
  <item name="category" xpath="./div[2]/div[1]//p/text()" strip></item>
</list>
```

This configuration will scrape news articles from pages 1 through 5 and extract relevant details such as URL, title, subtitle, date, view count, and category. -->


<!-- 
### Follow-up Requests

You can define follow-up scraping actions for specific items. For example, after scraping a list of locations, you may want to scrape detailed information from each location's page:
#### HTML Configuration

```html
<request url="https://badmintonclubs.org" parser="all-locations"></request>

<list
  xpath="//map/area"
  name="all-locations"
  key="href"
  follow-up-parser="location-page-parser"
  url-template="f'https://badmintonclubs.org{item['href']}'"
>
  <item
    name="name"
    xpath="@title"
    parse="value.split('badminton in ')[1] if value else None"
  ></item>
  <item name="href" xpath="@href"></item>
</list>

<list name="location-page-parser" xpath="//table//tr/td/a">
  <item name="name" xpath="text()"></item>
  <item name="location" xpath="../../td[2]/text()" strip></item>
  <item name="href" xpath="@href"></item>
  <item name="phone" xpath="../../td[3]/text()"></item>
  <item name="state" parse="request['meta']['name']"></item>
</list>

```

This configuration will first scrape the main list of locations and then follow up by scraping detailed information from each location's page, storing the results in `clubs.json`. -->


<!-- 
## Example Project

To better understand how HTMSParser works, you can refer to the following example project:

### Scraping Astronomy News

The following configuration scrapes astronomy news from `phys.org`, including handling pagination and outputting the data to a JSON file.

```html
<request-list
  start="1"
  end="12"
  url-template="f'https://www.astronomy.com/tags/news/page/{i}/'"
  parser="main-news"
></request-list>
<list name="main-news" xpath="//main/div/article" key="url">
  <item name="url" xpath=".//a/@href"></item>
  <item name="image_url" xpath=".//a/img/@src"></item>
  <item name="title" xpath="./header/h2/a/text()"></item>
</list>

<output path="astronomy_news.json" type="json" parser="main-news"></output>
```

This configuration will scrape all the news articles across 12 pages and save the results to `astronomy_news.json`. -->


<!-- 
## Contributing

Contributions to HTMSParser are welcome! Whether it's reporting a bug, suggesting a new feature, or submitting a pull request, your input is valuable.

### Steps to Contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request. -->
