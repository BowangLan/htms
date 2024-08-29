# HTMS: HTML-based Web Scraping Library

## Overview

HTMSLParser is a Python library for web scraping using an HTML-like configuration. It simplifies data extraction, handles pagination, and supports custom parsing, making it easy to gather structured data from websites with minimal coding.

## Features

- **Declarative Scraping Configuration:** Define scraping tasks using an HTML-like syntax to specify requests, lists, items, and outputs.
- **Pagination Handling:** Automatically manage pagination by defining start, end, and URL templates.
- **Follow-up Requests:** Enable follow-up scraping on specific items based on extracted data from initial requests.
- **Multiple Parsers:** Combine and use multiple parsers for complex scraping tasks.
- **Flexible Data Extraction:** Use XPath for precise data extraction, including support for custom parsing and filtering.
- **JSON Output:** Export scraped data directly to JSON files.
- **Item Data Manipulation:** Strip whitespace, parse data, and apply filters to extracted items.
- **Request Configuration:** Supports GET and POST methods with customizable headers.

## Installation

To install HTMSParser, simply clone the repository and include it in your project:

```bash
git clone https://github.com/yourusername/htms.git
```

<!-- TODO: Alternatively, you can install the package using `pip` if it is available on PyPI:

```bash
pip install HTMSparser
``` -->

## Run Examples

A list of example HTML files are included in this repo under `example_html` folder. To run these, use this command:

```
python -m htms.examples <example-file-name>
```

You can see a full list of example files using this command:

```
python -m htms.examples
```

## Usage

### Basic Example

Suppose you want to scrape badminton club locations from `badmintonclubs.org`. The following configuration will extract the name and href of each club listed on the site:

First, create an HTML file with the following content:

```html
<request url="https://badmintonclubs.org" parser="locations"></request>
<list xpath="//map/area" name="locations" key="href">
  <item
    name="name"
    xpath="@title"
    parse="value.split('badminton in ')[1] if value else None"
  ></item>
  <item name="href" xpath="@href"></item>
</list>
```

Next, run this command in the folder in which you cloned ths repo:

```
python -m htms <your-html-file>
```

Alternatively, you can use call the Python API to execute the scraping:

```python
from htms import HTMSParser

with open('config.html', 'r') as file:
    config = file.read()

parser = HTMSParser()
parser.feed(config)
parser.start()
```

## HTML Configuration

You can see a list of sample HTML configuration files under `sample_html` folder of this repo.

To run these examples, use this command:

```
python -m htms sample_html/<html-file-name>.html
```

### Handling Pagination

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

This configuration will scrape news articles from pages 1 through 5 and extract relevant details such as URL, title, subtitle, date, view count, and category.

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

<output path="./clubs.json" type="json" parser="location-page-parser"></output>
```

This configuration will first scrape the main list of locations and then follow up by scraping detailed information from each location's page, storing the results in `clubs.json`.

### Outputting Data

The data can be output to JSON files by defining an `output` tag in the HTML configuration:

#### HTML Configuration

```html
<output path="./output.json" type="json" parser="main-news"></output>
```

This will save the scraped data from the `main-news` parser to `output.json`.

### Custom Parsing and Filtering

HTMSParser supports custom parsing and filtering of data using Python expressions in the `parse` and `filter` attributes.

#### Example

```html
<item
  name="view_count"
  xpath="./div[2]/div[4]/p/span/text()"
  strip
  parse="int(value)"
></item>
<list name="nav-items" xpath="//nav/div[2]/div//a" filter="item['title'] != ''">
  <item name="url" xpath="@href"></item>
  <item name="title" xpath="text()" strip></item>
</list>
```

This configuration will parse the `view_count` as an integer and filter out any navigation items with an empty title.

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
