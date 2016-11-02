from scraper import *


ffbrowser = webdriver.Firefox(executable_path='/Applications/geckodriver')

ffbrowser.implicitly_wait(15) # seconds
ffbrowser.get('https://www.lyst.com/shop/mens/')

print(get_list_links(ffbrowser,'https://www.lyst.com/apc/'))

ffbrowser.quit()