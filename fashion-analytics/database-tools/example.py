from scraper import *

letter_to_scrape='B'
f = open('scrape_'+letter_to_scrape+'.log', 'a')

scraper_obj = Scraper()
scraper_obj.connect_database('fashion-items')

dbbrand = BrandsDatabase()
brands=dbbrand.get_brands_letter(letter_to_scrape)

count = 0
for i in brands:
    count=count+1
    if not i['scraped']:
        print(i['brand']+'. From letter '+letter_to_scrape+', brand '+ str(count)+' of '+str(len(brands)))
        response = scraper_obj.scrape_brand(i['url'])
        dbbrand.set_brand_scraped(i['brand-id'])
        f.write(response + "\n")
f.close()

