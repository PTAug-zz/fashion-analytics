from scraper import *

scraper_obj = Scraper()
tuple_list=scraper_obj.get_list_links_brand('https://www.lyst.com/apc/')
for cat_brand in tuple_list:
    prod_dics = scraper_obj.create_products_records(cat_brand)
    print(prod_dics)