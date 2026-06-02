# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class QuestionItem(scrapy.Item):
    title = scrapy.Field()
    tags = scrapy.Field()
    votes = scrapy.Field()
    answers = scrapy.Field()
    date = scrapy.Field()
    user = scrapy.Field()
    
class UserItem(scrapy.Item):
    username = scrapy.Field()
    reputation = scrapy.Field()
    gold = scrapy.Field()
    silver = scrapy.Field()
    bronze = scrapy.Field()
    profile_views = scrapy.Field()
    active_days = scrapy.Field()
    member_since = scrapy.Field()
    last_seen = scrapy.Field()