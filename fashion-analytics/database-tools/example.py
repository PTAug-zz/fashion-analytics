from scraper import *
from dynamointerface import *

scraper_obj = Scraper()
tuple_list=scraper_obj.get_list_links_brand('https://www.lyst.com/apc/')

fbd=FashionDatabase()

for cat_brand in tuple_list:
    prod_dics = scraper_obj.create_products_records(cat_brand)
    for d in prod_dics:
        fbd.add_item(d)