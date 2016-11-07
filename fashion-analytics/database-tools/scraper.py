import time
from utils import *
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import namedtuple

Category = namedtuple('Category', 'category subcategory link')

class Scraper:
    def __init__(self):
        self.browser= webdriver.Firefox(executable_path=
                                        '/Applications/geckodriver')
        self.browser.implicitly_wait(15)  # seconds
        self.browser.get('https://www.lyst.com/shop/mens/')

    def get_list_links_brand(self,url:str):
        """
        Returns the full list of category, subcategory and link, in the form of a
        list of tuples of form:

        (category, subcategory, link)

        The link voluntarily omits https://www.lyst.com.
        """
        self.browser.get(url)
        self.browser.find_element_by_id("Clothing")
        page_soup_xml=BeautifulSoup(self.browser.page_source,'lxml')

        all_cat = page_soup_xml.find('div',
                        {'class': 'universal-filter-category'}).find_all('div',
                        {'class': 'universal-filter-category'})
        all_sub = {}
        for i in all_cat:
            subcat = {}
            for l in i.find('div', {'class':
                    'universal-filter-category__children'}).find_all('label'):
                subcat[l.text.strip('\n ')] = {'link': l.find('input')
                                                                .get('value')}
            sub_dic = {
                "link": i.find('input').get('value'),
                "subcat": subcat
            }
            all_sub[i.find('label').text.strip('\n ')] = sub_dic

        list_links=[]
        for category in all_sub:
            for subcategory in all_sub[category]['subcat']:
                list_links.append(Category(category,subcategory,url+
                    "?category="+all_sub[category]['link']+"&subcategory="+
                    "+".join(all_sub[category]['subcat'][subcategory]
                                                    ['link'].split(" "))))
        return list_links

    def get_to_bottom_page(self):
        """
        Returns the full page (scrolled to the bottom). The page
        returned is in XML format.

        The input url should omit www.lyst.com. (www.lyst.com[/url])

        This function still has some problems, sometimes it doesn't
        fully scroll to the bottom. It can do it, but I still have to
        debug it, it's a weird error.
        """
        import numpy as np
        print("Trying to get to bottom of "+self.browser.current_url)
        last_height = self.browser.execute_script(
                                    "return document.body.scrollHeight")
        while True:
            self.browser.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(np.random.uniform(3,3.5))
            new_height = self.browser.execute_script("return "
                                                "document.body.scrollHeight")
            print("Length of page: "+str(last_height)+" -> "+str(new_height))
            if new_height == last_height:
                break
            last_height = new_height
        print("Finished")

    def save_lyst_subcategory_page(self,cat_obj:Category):
        """
        This function needs an instance of a Selenium Webdriver called browser
        to be open.

        It takes the input tuple of a subcategory, loads the page from Lyst,
        goes to the bottom of the page (with the function get_to_bottom_page
        executed three times because it sometimes randomly stops), and save
        the whole html of the page in a .webpage file named after the
        subcategory.

        It also returns the final length of the webpage as a metric to know if
        the scrolling went well.

        cat_tuple is a tuple (category, subcategory, link) returned
        by the get_list_links function.
        """
        print("Loading the page "+cat_obj.subcategory+"...")
        self.browser.get(cat_obj.link)
        self.get_to_bottom_page()
        time.sleep(5)
        self.get_to_bottom_page()
        time.sleep(5)
        self.get_to_bottom_page()
        name_file_subcat='_'.join(cat_obj.subcategory.split(' ')).lower()\
                         +".webpage"
        write_in_file(name_file_subcat,self.browser.page_source)
        print('\n\n')
        return self.browser.execute_script("return document.body.scrollHeight")

    def scrape_all_category_pages(self,url):
        list_length=[]
        list_links=self.get_list_links_brand(url)
        for subcat in list_links:
            curr=self.save_lyst_subcategory_page(subcat)
            list_length.append((subcat.link,curr))

    def create_products_records(self,cat_obj:Category):
        self.browser.get(cat_obj.link)
        self.get_to_bottom_page()
        time.sleep(5)
        self.get_to_bottom_page()
        time.sleep(5)
        self.get_to_bottom_page()
        page_soup_xml = BeautifulSoup(self.browser.page_source,'lxml')
        articles_record=list()
        for prod in page_soup_xml.find('div',
                    {'class':'product-feed__segment-items'}).find_all('div',
                                                  {'class':'product-card'}):
            dic=dict()
            dic['short_description']=prod.find('div',
                                          {"itemprop":"name"}).get_text()
            dic['brand']=prod.find('div',
                        {"class":"product-card__designer"}).get_text().strip()
            dic['mens-women']='mens'
            dic['category']=cat_obj.category
            dic['subcategory']=cat_obj.subcategory
            dic['url']='https://www.lyst.com'+prod.find('a',
                                          {"itemprop":"url"}).get('href')
            dic['image-url'] = prod.find('img',
                                        {"itemprop": "image"}).get('src')
            dic['currency'] = prod.find('link',
                                {"itemprop": "priceCurrency"}).get('content')
            dic['price'] = prod.find('link',
                                {"itemprop": "price"}).get('content')
            articles_record.append(dic)
        return articles_record

    def __del__(self):
        print("Scraper object deleted, closing the browser...")
        self.browser.quit()