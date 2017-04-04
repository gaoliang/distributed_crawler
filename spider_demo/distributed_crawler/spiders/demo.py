import scrapy
import re
class BiliIndex(scrapy.Spider):
    name = "anime"
    allowed_domains = []

    def start_requests(self):
        for num in range(1,141):
            yield scrapy.Request(
                "http://bangumi.bilibili.com/web_api/season/index_global?page={}&page_size=20&version=0&is_finish=0&start_year=0&tag_id=&index_type=1&index_sort=0&quarter=0".format(
                    num), callback=self.parse)

    def parse(self, response):
        for x in re.findall('season\_id\"\:\"([\d]{1,6})\"', response.text):
            href = "http://bangumi.bilibili.com/anime/" + x
            yield scrapy.Request(href, callback=self.parse2)

    def parse2(self, response):
        item = {}
        base_xpath = response.xpath('//div[@class="bangumi-info-r"]')
        info_title = base_xpath.xpath("//h1/text()").extract()
        info_style_item = base_xpath.xpath(
            './/span[@class="info-style-item"]/text()').extract()
        info_count_item_play = base_xpath.xpath(
            './/span[@class="info-count-item info-count-item-play"]/em/text()').extract()
        info_count_item_fans = base_xpath.xpath(
            './/span[@class="info-count-item info-count-item-fans"]/em/text()').extract()
        info_count_item_review = base_xpath.xpath(
            './/span[@class="info-count-item info-count-item-review"]/em/text()').extract()
        info_update = base_xpath.xpath(
            './/div[@class="info-row info-update"]/em/span/text()').extract()
        info_cv = base_xpath.xpath(
            './/div[@class="info-row info-cv"]/em/span/text()').extract()
        info_desc_wrp = base_xpath.xpath(
            './/div[@class="info-row info-desc-wrp"]/div[@class="info-desc"]/text()').extract()

        item['info_title'] = info_title
        item['info_style_item'] = info_style_item
        item['info_count_item_play'] = info_count_item_play
        item['info_count_item_fans'] = info_count_item_fans
        item['info_count_item_review'] = info_count_item_review
        item['info_update'] = info_update
        item['info_cv'] = info_cv
        item['info_desc_wrp'] = info_desc_wrp
        yield item