import time
from collections import namedtuple
import selenium
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver, common
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from dynamointerface import *

Category = namedtuple('Category', 'category subcategory link')


class Scraper:
    """Lyst scraping interface class.

    This class automates the scraping of the Lyst fashion website
    and the optional update of an AWS DynamoDB fashion articles
    database. The `scrape_brand` function scrapes a brand located
    at the given url, and puts the articles on the database. The
    `create_products_record` function gives a list of products
    as dictionaries.

    .. warning:: If the interface with AWS is used, AWS has to be
    configured. Run ``aws configure`` in a shell.
    """

    def __init__(self, config='AWS'):
        """Construct a Scraper object according to the config given.

        If the config is 'AWS' (default), sets up the in-class
        browser for AWS, if 'MAC', sets up the object for a mac.

        :param config: system used, 'MAC' or 'AWS' (default)
        :type config: str
        """
        if config == 'MAC':
            self.browser = selenium.webdriver.Firefox(executable_path=
                                                '/Applications/geckodriver')
        if config == 'AWS':
            self.display = Display(visible=0, size=(1900, 1200))
            self.display.start()
            binary = FirefoxBinary('/home/ec2-user/firefox/firefox')
            self.browser = webdriver.Firefox(firefox_binary=binary,
                                executable_path='/home/ec2-user/geckodriver')
        else:
            raise ValueError('The config does not exist.')
        self.browser.implicitly_wait(5)  # seconds
        self.browser.get('https://www.lyst.com/shop/mens/')

    def fill_brands_database(self, name):
        fashiondb = BrandsDatabase(name)
        self.browser.get('https://www.lyst.com/designers/')
        page_soup_xml = BeautifulSoup(self.browser.page_source, 'lxml')

        for letter in page_soup_xml.find_all('div', {
            'class': 'brands-layout__az-block'}):
            for brand in letter.find_all('a'):
                dic = dict()
                dic['letter'] = letter.get('id')
                dic['brand'] = brand.get_text()
                dic['url'] = 'https://www.lyst.com' + brand.get('href')
                dic['scraped'] = False

                print(dic['letter'], dic['brand'], dic['url'])

                dic['brand-id'] = datetime.now().strftime('%m%d%H%M%S') + '-' \
                                  + format(random.randint(0, 9999), "04")
                fashiondb.db.put_item(Item=dic)

    def connect_database(self, name='fashion-items'):
        """Connect to the database of given :param name:"""
        self.fdb = FashionDatabase(name)

    def get_list_links_brand(self, url: str):
        """Get all categories and subcategories of a brand

        Returns the full list of Category objects for the
        brand of which the url on Lyst is given.

        :param url: URL of the brand on Lyst
        :return: list of Category for the brand.
        :rtype: list of Category
        """
        self.browser.get(url)
        try:
            self.browser.find_element_by_id("Clothing")
        except selenium.common.exceptions.NoSuchElementException as err:
            print('No Clothing section to get categories from. Aborting.')
            return None
        page_soup_xml = BeautifulSoup(self.browser.page_source, 'lxml')

        all_cat = page_soup_xml.find('div',
                            {'class': 'universal-filter-category'}).find_all(
                            'div', {'class': 'universal-filter-category'})
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

        list_links = []
        for category in all_sub:
            for subcategory in all_sub[category]['subcat']:
                list_links.append(Category(category, subcategory, url +
                                           "?category=" + all_sub[category][
                                               'link'] + "&subcategory=" +
                                           "+".join(
                                               all_sub[category]['subcat'][
                                                   subcategory]
                                               ['link'].split(" "))))
        return list_links

    def get_to_bottom_page(self):
        """Scroll to the bottom of the current page.

        Scroll to the bottom of the page loaded in the in-class
        browser.
        """
        print("Scrolling to the bottom of " + self.browser.current_url)
        last_height = self.browser.execute_script(
            "return document.body.scrollHeight")

        # Do it twice because it randomly stops sometimes (rare)
        for j in range(2):
            while True:
                self.browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = self.browser.execute_script("return "
                                                "document.body.scrollHeight")
                print("Length of page: " + str(last_height) + " -> " + str(
                    new_height),
                      end='\r')
                if new_height == last_height:
                    break
                last_height = new_height
            time.sleep(2)


    def create_products_records(self, cat_obj: Category):
        """Get all articles of given Category object.

        The dictionaries returned (one for each product) contain the
        following attributes: `short_description`, `brand`, `url`
        `men-women`, `category`, `subcategory`, `image-url`,
        `currency`, `price`.

        :param cat_obj: Category object from which to get articles.
        :type cat_obj: Category
        :return: list of dict, each containing a product's attributes
        :rtype: list of dict
        """
        self.browser.get(cat_obj.link)
        self.get_to_bottom_page()

        page_soup_xml = BeautifulSoup(self.browser.page_source, 'lxml')
        articles_record = list()
        pcards = page_soup_xml.find('div', {'class':
                                                'product-feed__segment-items'})
        if pcards is not None:
            for prod in pcards.find_all('div', {'class': 'product-card'}):
                if not prod.find('span',
                                 {'class': 'product-card__sold-out-message'}):
                    dic = dict()
                    dic['short_description'] = prod.find('div',
                                            {"itemprop": "name"}).get_text()
                    dic['brand'] = prod.find('div',
                        {"class": "product-card__designer"}).get_text().strip()
                    dic['men-women'] = 'men'
                    dic['category'] = cat_obj.category
                    dic['subcategory'] = cat_obj.subcategory
                    dic['url'] = 'https://www.lyst.com' + prod.find('a',
                                            {"itemprop": "url"}).get('href')
                    dic['image-url'] = prod.find('img').get('image-src')
                    dic['currency'] = prod.find('link',
                                {"itemprop": "priceCurrency"}).get('content')
                    dic['price'] = prod.find('link',
                                        {"itemprop": "price"}).get('content')
                    articles_record.append(dic)
        return articles_record

    def scrape_brand(self, url):
        """Scrape a brand and put its articles in the database.

        Puts every product of a brand in the connected database,
        and returns a log message to know if some items of the
        brand are effectively put in the database.

        :param url: URL of the brand on Lyst
        :type url: str
        :return: debug string, signals the absence of products
        :rtype: str

        .. note:: the database has to be connected to run this
            method.
        """
        tuple_list = self.get_list_links_brand(url)
        if tuple_list is None:
            return "Can't scrape" + url + ". Check if there's a Clothing id."
        for cat_brand in tuple_list:
            prod_dics = self.create_products_records(cat_brand)
            if prod_dics:
                for d in prod_dics:
                    self.fdb.add_item(d)
        return 'OK ' + url

    def __del__(self):
        """Close the browser when finished"""
        print("Scraper object deleted, closing the browser...")
        self.browser.quit()
