from scraper import *

#display = Display(visible=0, size=(800, 600))
scraper_obj = Scraper()

print(scraper_obj.get_list_links('https://www.lyst.com/apc/'))