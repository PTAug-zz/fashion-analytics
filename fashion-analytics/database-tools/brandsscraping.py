from selenium import webdriver
import boto3
from datetime import datetime
import random
from bs4 import BeautifulSoup

browser = webdriver.Firefox(executable_path='/Applications/geckodriver')
browser.implicitly_wait(15)  # seconds
browser.get('https://www.lyst.com/shop/mens/')

dynamodb = boto3.resource('dynamodb')
db = dynamodb.Table('brands-scraping')
print(db.creation_date_time)

browser.get('https://www.lyst.com/designers/')
page_soup_xml = BeautifulSoup(browser.page_source,'lxml')
articles_record=list()

for letter in page_soup_xml.find_all('div',{'class': 'brands-layout__az-block'}):
    for brand in letter.find_all('a'):
        dic = dict()
        dic['letter'] = letter.get('id')
        dic['brand'] = brand.get_text()
        dic['url'] = 'https://www.lyst.com'+brand.get('href')
        dic['scraped'] = False

        print(dic['letter'],dic['brand'],dic['url'])

        dic['brand-id'] = datetime.now().strftime('%m%d%H%M%S') + '-' + \
                         format(random.randint(0, 9999), "04")
        db.put_item(Item=dic)
browser.quit()