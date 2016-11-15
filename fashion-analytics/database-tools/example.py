from scraper import *


f = open('scrape_a.log', 'a')

scraper_obj = Scraper()
scraper_obj.connect_database('fashion-items')

dbbrand = BrandsDatabase()
brands=dbbrand.get_brands_letter('A')

for i in brands:
    if not i['scraped']:
        response = scraper_obj.scrape_brand(i['url'])
        dbbrand.set_brand_scraped(i['brand-id'])
        f.write(response + "\n")

f.close()