from scraper import *

scraper_obj = Scraper()
scraper_obj.connect_database('fashion-items')
scraper_obj.scrape_brand('https://www.lyst.com/a-bathing-ape/')