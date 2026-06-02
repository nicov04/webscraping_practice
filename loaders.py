

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Identity
from .items import QuestionItem, UserItem
from datetime import datetime
import re

## Helper functions for question loader
def clean_tag(tag):
    #clean up formating, "web-scraping" to "Web Scraping"
    tag = tag.replace('-', ' ').title() #replace hyphens with spaces, .title() capitalises each letter of each word
    return tag 

def clean_user(text):
    #deal with extra whitespaces or empty values
    #returns none if text is empty, better for analysis
    text = text.strip()
    return text if text else None #return none if empty

def parse_date(date_str):
    #convert date string into ISO format
    #can actually parse, standardized and it works with pandas
    date_str = date_str.lower().replace('asked', '').replace('answered', '') #these words come with the date, we remove them as the parser ddoesn't understand them
    #strptime = string parse time, converts string to datetime object
    #strftime = strip format time, converts datetime to string
    return datetime.strptime(date_str, "%b %d '%y at %H:%M").strftime("%Y-%m-%dT%H:%M:%S")
    #ISO format: yyyy-mm-ddthh:mm:ss

class QuestionLoader(ItemLoader):
    #loader for QuestionItem for automatic data cleaning
    # when you call loader.add_css("title", ...) it runs through processors
    #_in processors clean data as it comes in
    #_out processors format data when load_item() is called
    
    default_item_class = QuestionItem

    #takefirst() - if multiple values are found, take only hte first
    #because most fields should be single value (one title/date/etc...)
    default_output_processor = TakeFirst()
    
    #exception, tags should keep all values (questions have multiple tags)
    #identity() means dont multify, keep as list
    tags_out = Identity()
    
    
    tags_in = MapCompose(clean_tag) #clean each tag
    votes_in = MapCompose(int) #convert vote to integer
    answers_in = MapCompose(int)#convert answers to integer
    date_in = MapCompose(parse_date) #convert date to ISO format
    user_in = MapCompose(clean_user) #clean username
    
    
## Helper functions for user loader
def to_int(text):
    #convert text to integer, handling commas and empty values
    #eg "1,234" to "1234" and "" to "0"
    #^ because numbers on website have comma separations
    
    if not text:
        return 0 #default to 0 if empty, avoid breaking the code
    return int(text.replace(',', '').strip())    
    # remove commas and extra whitespace, then convert to int
    
    
def extract_views(text):
    #extract number from text, like "profile viewed 1234 times"
    #only need the number
    
    match = re.search(r"([\d,]+)", text) #expression to find digits, [\d,]+ means one or more digits or commas
    return int(match.group(1).replace(",", "")) if match else 0
    ##used ai here because i knew there was a way to make it a one liner but wasnt sure and short on time
    #the return function extracts the matched number and removes commas, defaults if no number is found (return.. else 0)


def parse_member_since(text): 
    #January 15 2025 -> datetime 
    return datetime.strptime(text.strip(), "%B %d %Y")

def parse_last_seen(text):
    #January 15 '24 at 14:30 -> datetime 
    return datetime.strptime(text.strip(), "%b %d '%y at %H:%M")

def compute_active_days(values): #bit of math to find how long they had the account for
    member_since, last_seen = values
    return (last_seen.date() - member_since.date()).days

class UserLoader(ItemLoader):
    #loader for UserItem    
    default_item_class = UserItem
    default_output_processor = TakeFirst() #similar functionality to QuestionLoader
    
    
    reputation_in = MapCompose(to_int)
    gold_in = MapCompose(to_int)
    silver_in = MapCompose(to_int)
    bronze_in = MapCompose(to_int)
    profile_views_in = MapCompose(extract_views)
    
    #parse dates into datetime for calculation
    member_since_in = MapCompose(parse_member_since)
    last_seen_in = MapCompose(parse_last_seen)
    
    
    





