import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from kbstar.items import Article


class kbstarSpider(scrapy.Spider):
    name = 'kbstar'
    start_urls = ['https://otalk.kbstar.com/quics?page=C019391&QSL=F']

    def parse(self, response):
        links = response.xpath('//dt/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//dl[@class="blog_title"]/dt/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="location"]/em/text()').get()
        if date and date.strip():
            date = " ".join(date.split())
        else:
            return

        content = response.xpath('//div[contains(@class, "blog")]/dl/dd[1]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
