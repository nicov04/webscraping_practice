
import scrapy
from BookScraper.items import QuestionItem
from BookScraper.loaders import QuestionLoader



class QuestionSpider(scrapy.Spider):
    
    """
    spider for stack overflow - assigned to Christianity
    spider has a two step process
    1. parse() gets a list of questions, votes and answers
    2. parse_question() visits each question page for more details (title, tags, user, date)
    """
    
    
    name = "question" #name you call to run the spider
    allowed_domain = ["192.168.0.3"] #restrict crawling to specific domain
    start_urls = ["http://192.168.0.3:9123/christianity.stackexchange.com_en_all_2025-12/questions"] #inital page to start the scraping
    
    def parse (self, response):
        """
        parsing question list page
        we are double parsing because pages with questions dont have all the details we need
        so we need to visit an individual page for the details
        
        """
        
        #loops through every question on the list page
        # css selector then finds each question container div
        
        for q in response.css("div.question-summary"):
            link = q.css("a.question-hyperlink::attr(href)").get() #link of full question page
            answers = q.css("div.status strong::text").get() #::attr(href) extracts the href  value
            votes = q.css("div.vote span strong::text").get() #vote from vote counter..
            
            
            # response.follow() makes an new request to the question page
            yield response.follow( ###
                link,
                callback = self.parse_question, #calling this func once page loads
                meta = {"answers" : answers, "votes": votes}) #passing data on to the next parser
            #meta makes is so that we dont need to extract them again on a different page or make them again
            
            
        next_page = response.css("a[rel='next']::attr(href)").get() #finding next page link if it exists
        if next_page: #follow the link and parse() again
            yield response.follow(next_page, callback = self.parse) #parsing loop
            
    
    def parse_question(self, response):
        
        """
        parse individual question page for details
        need a different function for this as the detail page is different to the question one, so new css/xpath
        """
        
        #itemloader organises and cleans data before saving
        #loader automatically cleans data and processing
        loader = QuestionLoader(item=QuestionItem(), selector=response)
        
        #gets question title from header
        loader.add_css("title", "#question-header h1 a::text")
        
        #::text because we want the content and not whole <a> element
        loader.add_css("tags", "a.post-tag::text")
        
        #date/time the question was posted
        loader.add_css("date", "div.post-signature.owner time::text")
        
        #get username of who asked the question
        #used xpath instead of css because the information was nested in a weird way
        #needed to find specific user card which contains an 'asked' timestamp(not 'answered')
###
        loader.add_xpath(
            "user",
            "//div[contains(@class, 's-user-card')][.//time[start-with(@datetime,'asked')]]",
            "//a[contains(@class, 'a-user-card--link')]/text()")
        
        #get votes and answeres we passed from parse()
        #add_value because we already have this data, not extracting from response
        loader.add_value("votes", response.meta["votes"])
        loader.add_value("answers", response.meta["answers"])
        
        #load_item() processes all fields and returns the final item
        yield loader.load_item()