from scraper import *

scraper_obj = Scraper()
tuple_list=scraper_obj.get_list_links_brand('https://www.lyst.com/apc/')
scraper_obj.save_lyst_subcategory_page(tuple_list[1])