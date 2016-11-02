import re
import requests
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver

def get_list_links(browser,url:str):
    """
    Returns the full list of category, subcategory and link, in the form of a
    list of tuples of form:
    
    (category, subcategory, link)
    
    The link voluntarily omits https://www.lyst.com.
    """
    browser.get(url)
    browser.find_element_by_id("Clothing")
    page_soup_xml=BeautifulSoup(browser.page_source,'lxml')

    all_cat = page_soup_xml.find('div', {'class': 'universal-filter-category'}).find_all('div', {'class': 'universal-filter-category'})
    all_sub = {}
    for i in all_cat:
        subcat = {}
        for l in i.find('div', {'class': 'universal-filter-category__children'}).find_all('label'):
            subcat[l.text.strip('\n ')] = {'link': l.find('input').get('value')}
        sub_dic = {
            "link": i.find('input').get('value'),
            "subcat": subcat
        }
        all_sub[i.find('label').text.strip('\n ')] = sub_dic

    list_links=[]
    for category in all_sub:
        for subcategory in all_sub[category]['subcat']:
            list_links.append((category,subcategory,
                   url+"?category="+all_sub[category]['link']+
                  "&subcategory="+"+".join(all_sub[category]['subcat'][subcategory]['link'].split(" "))))
    return list_links

def get_to_bottom_page(browser):
    """
    Returns the full page (scrolled to the bottom). The page
    returned is in XML format.
    
    The input url should omit www.lyst.com. (www.lyst.com[/url])
    
    This function still has some problems, sometimes it doesn't
    fully scroll to the bottom. It can do it, but I still have to
    debug it, it's a weird error.
    """
    import numpy as np
    print("Trying to get to bottom of "+browser.current_url)
    lastHeight = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(np.random.uniform(3,3.5))
        newHeight = browser.execute_script("return document.body.scrollHeight")
        print("Length of page: "+str(lastHeight)+" -> "+str(newHeight))
        if newHeight == lastHeight:
            break
        lastHeight = newHeight
    print("Finished")

def write_in_file(name_of_file:str,content):
    """
    Writes the content in a file of name name_of_file.
    """
    print("Creation of file "+name_of_file)
    file = open(name_of_file, "w")
    print("Writing...")
    file.write(content)
    file.close()
    print("Saving in file successful!")

def save_lyst_subcategory_page(browser,cat_tuple):
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
    print("Loading the page "+cat_tuple[1]+"...")
    browser.get('https://www.lyst.com'+cat_tuple[2])
    get_to_bottom_page(browser)
    time.sleep(5)
    get_to_bottom_page(browser)
    time.sleep(5)
    get_to_bottom_page(browser)
    name_file_subcat='_'.join(cat_tuple[1].split(' ')).lower()+".webpage"
    write_in_file(name_file_subcat,browser.page_source)
    print('\n\n')
    return browser.execute_script("return document.body.scrollHeight")

def get_soup_from_file(filename:str):
    """
    Returns the BeautifulSoup object from the .webpage file loaded.
    """
    f = open(filename, 'r')
    read_page=f.read()
    page_soup_xml=BeautifulSoup(read_page,'lxml')
    return page_soup_xml

def scrape_all_category_pages(url):
    browser = webdriver.PhantomJS(executable_path='/Applications/phantomjs')
    list_length=[]
    list_links=get_list_links(browser,url)
    for subcat in list_links:
        curr=save_lyst_subcategory_page(browser,subcat)
        list_length.append((subcat[2],curr))