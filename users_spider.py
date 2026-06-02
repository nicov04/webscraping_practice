
import scrapy
from BookScraper.items import UserItem
from BookScraper.loaders import UserLoader

class UserSpider(scrapy.Spider):
    """
    spider to scrape user profile data
    two step process
    1. parse() ets user list with username, reputation, badges
    2. parse_profile() vosits profile for more info, views, member since and last seen
    
    """
    
    name = "users" #spider name
    allowed_domain = ["192.168.0.3"]
    start_urls = ["http://192.168.0.3:9123/christianity.stackexchange.com_en_all_2025-12/users"]
    
    def parse(self, response):
        """
        parse the users list page
        it has two steps because one page has only reputation and badges
        but each profile has more info that we need, like last seen, views and member since
        
        """
        
        #loop through each user on the list page
        for user in response.css("div.user-details"):
            
            #start collecting user data
            #get more later
            loader = UserLoader(item=UserItem(), selector=user)
            
            loader.add_css("username", "a::text")
            loader.add_css("reputation", "span.reputation-score::text")
            loader.add_css("gold", "span.badge1 + span.badgecount::text") #badges are grouped, badge icon + count
            loader.add_css("silver", "span.badge2 + span.badgecount::text")
            loader.add_css("bronze", "span.badge3 + span.badgecount::text")
            
            #the link to user's full profile page
            profile_url = user.css("a::attr(href)").get()
            
            #visit the user's profile to get more details
            yield response.follow(
                profile_url,
                callback = self.parse_profile,
                meta = {"loader": loader}) #passing a partially filled loader
            #we'll add more fielnds on the profile page
            
            #find next page of users
            next_page = response.css("a[rel='next']::attr(href)").get()
            
            if next_page: #continue to the next page of user list
                yield response.follow(next_page, callback = self.parse)
                
    
    def parse_profile(self, response):
        """
        parsing individual user page
        combining data from user list
        """
        
        #previous loader we made
        #we retrieve the  from meta because it already has username, rep and badges
        
        loader = response.meta["loader"]
        
        #we update the selector because we're now on a different page
        loader.selector = response
        
        
        #xpath because complex html layout
        #we need to find specific icons nad then navigate to their associated text
        #profile views - find eye icon, go the parent <li> then find the text
        #ancestor::li does that
        
        loader.add_xpath("profile_views", "//svg[contains(@class, 'iconEye')]/ancestor::li//div[contains(@class, 'fill')]/text()")
        
        #member since date - find history icon, get associated date text
    
        loader.add_xpath("member_since", "//svg[contains(@class, 'iconHistory')]/ancestor::li//span/text()")
        
        #last seen date- find clock icon, get text
        loader.add_xpath("last_seen", "//svg[contains(@class, 'iconClock')]/ancestor::li//span/text()")
        
        ##calculating active days
        #take the values we just etracted (already processed by loader)
        #get_collected_values helps calculate from these fields
        
        member_since_val = loader.get_collected_values("member_since")
        last_seen_val = loader.get_collected_values("last_seen")
        
        #only calculate if we have both dates 
        #check to prevent errors if dates are missing
        if member_since_val and last_seen_val:
            #calculate days between member_since and last_seen
            #.date() converts datetime to date for substraction
            #.days gets the result as number of days
            
            active_days = (last_seen_val[0].date() - member_since_val[0].date()).days
            
            #add calculated value to item
            loader.add_value("active_days", active_days)
            
            #we have all fields from list page, from proifle page and calculated
        yield loader.load_item()
        
        
        