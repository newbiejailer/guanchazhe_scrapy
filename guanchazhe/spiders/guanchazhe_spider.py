from scrapy import Spider, Request
from guanchazhe.items import GuanchazheItem
from urllib.parse import urlencode
import json
import re


class Guanchazhe(Spider):
    name = 'guanchazhe'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    start_urls = ['https://www.guancha.cn']
    allowed_domains = ['guancha.cn']
    categories = ['国际', '军事', '财经', '产经', '科技', '智库前沿', '视频']
    # categories = ['国际']

    def parse(self, response):
        for cate in self.categories:
            temp_url = response.xpath('//a[@title="%s"]/@href' % cate).extract_first()
            cate_url = response.url + temp_url
            yield Request(url=cate_url, meta={'cate': cate}, callback=self.find_more)

    def find_more(self, response):
        cate = response.meta['cate']
        temp_url = response.xpath('//a[text()="更多"]/@href').extract_first()
        news_list_url = self.start_urls[0] + temp_url
        yield Request(url=news_list_url, meta={'cate': cate}, callback=self.parse_news_list)

    def parse_news_list(self, response):
        news = response.xpath('//ul[@class="column-list fix"]/li')
        for new in news:
            temp_url = new.xpath('./h4/a/@href').extract_first()
            page_url = self.start_urls[0] + temp_url
            yield Request(url=page_url, meta={'cate': response.meta['cate']}, callback=self.parse_page)

        for i in range(2, 11):
            next_url = re.sub(r'list_\d.shtml', 'list_%d.shtml' % i, response.url)
            yield Request(url=next_url, meta={'cate': response.meta['cate']}, callback=self.parse_news_list)

    def parse_page(self, response):
        title = response.xpath('head/title/text()').extract_first()
        doc_id = response.xpath('head/script[contains(text(), "_DOC_ID")]/text()').re_first(r'_DOC_ID="(\d+)"')
        pageNo = 1
        querystring = {
            'codeId': doc_id,
            'pageNo': pageNo,
            'codeType': 1,
            'order': 1,
            'ff': 'www'
        }
        comment_url = 'https://user.guancha.cn/comment/cmt-list.json?' + urlencode(querystring)
        yield Request(url=comment_url, meta={'cate': response.meta['cate'], 'title': title}, callback=self.parse_comments)

    def parse_comments(self, response):
        item = GuanchazheItem()
        item['cate'] = response.meta['cate']
        item['title'] = response.meta['title']
        comments = json.loads(response.body)['items']
        if comments:
            for comment in comments:
                item['user_name'] = comment['user_nick']
                item['comment_text'] = comment['content']
                item['tread_num'] = comment['tread_num']
                item['praise_num'] = comment['praise_num']
                yield item

            pageNo = re.search(r'pageNo=(\d+)', response.url).group(1)
            pageNo = 'pageNo=' + str(int(pageNo) + 1)
            next_url = re.sub(r'pageNo=\d+', pageNo, response.url)
            yield Request(url=next_url, meta={'cate': response.meta['cate'], 'title': response.meta['title']}, callback=self.parse_comments)


