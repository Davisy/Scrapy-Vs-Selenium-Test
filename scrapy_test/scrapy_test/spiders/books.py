import pandas as pd
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
import time
import resource


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def start_requests(self):
        URL = "https://books.toscrape.com/"
        yield scrapy.Request(url=URL, callback=self.response_parser)

    def response_parser(self, response):
        for selector in response.css("article.product_pod"):
            yield {
                "title": selector.css("h3 > a::attr(title)").extract_first(),
                "price": selector.css(".price_color::text").extract_first(),
            }

        next_page_link = response.css("li.next a::attr(href)").extract_first()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.response_parser)


def book_spider_result():
    start_time = time.time()
    books_results = []

    def crawler_results(item):
        books_results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)
    crawler_process = CrawlerProcess()
    crawler_process.crawl(BooksSpider)
    crawler_process.start()
    duration = time.time() - start_time
    return books_results, duration


books_data, scraping_duration = book_spider_result()

df = pd.DataFrame(books_data)
df.to_csv("books_data.csv", index=False)

memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (
    1024 * 1024
)  # Convert to MB
print(f"Scraping duration: {scraping_duration} seconds")
print(f"Memory used: {memory_usage} MB")
