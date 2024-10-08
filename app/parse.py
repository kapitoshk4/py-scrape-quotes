import csv
import logging
import sys
from dataclasses import dataclass, fields
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def fetch_html(url: str) -> str:
    with httpx.Client() as client:
        response = client.get(url)
        return response.text


def parse_single_quote(parse_soup: BeautifulSoup) -> Quote:
    tags = [tag.text for tag in parse_soup.select(".tag")]
    return Quote(
        text=parse_soup.select_one(".text").text,
        author=parse_soup.select_one(".author").text,
        tags=tags
    )


def parse_single_page_quotes(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    all_quotes = []
    page_url = BASE_URL
    while page_url:
        logging.info(f"Start parsing {page_url}")
        page = fetch_html(page_url)
        soup = BeautifulSoup(page, "html.parser")

        all_quotes.extend(parse_single_page_quotes(soup))

        next_button = soup.select_one("li.next > a")

        if next_button:
            next_page = next_button["href"]
            page_url = urljoin(BASE_URL, next_page)
        else:
            page_url = None

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            formatted_quote = (quote.text, quote.author, str(quote.tags))
            writer.writerow(formatted_quote)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
