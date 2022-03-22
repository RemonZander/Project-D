from email.mime import image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests

def scrape_page_layout_one(n):
    #GET LIST OF ALL ITEMS
    items = driver.find_elements(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product)")
    #print(f"length: {len(items)}")
    #print(f"page: {n}")

    page = driver.find_element(By.CSS_SELECTOR, ".is-active > span").text
    

    for item in items:
        #RETRIEVE NAME
        #name = item.find_element(By.CSS_SELECTOR, ".product-item__content > .product-item__info > .product-title--inline").text
        #TRY-BLOCK FOR INCONSISTENCY PRODUCT IMAGES PLACEMENT IN WEBELEMENT
        try:
            image_link = item.find_element(By.CSS_SELECTOR, ".product-item__image > div > a > img").get_attribute("src")
        except:
            image_link = item.find_element(By.CSS_SELECTOR, ".product-item__image > div > a > .skeleton-image > div > img")
            if image_link.get_attribute("src") is None:
               # print("CANNOT FIND SRC IN ELEMENT, TRYING ALTERNATIVE")
                #for attr in range(len(image_link.get_property("attributes"))):
                    #print(f"INDEX: {attr},\n {image_link.get_property('attributes')[attr]}\n\n")
                image_link = image_link.get_property("attributes")[1]["value"]
                #print("FOUND IMAGE LINK" + image_link)
            else:
                image_link = image_link.get_attribute("src")

        #TODO: BOTH LINK AND NAME CAN BE FOUND IN SAME CLASSES, CAN IMPROVE THIS FOR CLARITY
        #product_link = item.find_element(By.CSS_SELECTOR, ".product-item__content > .product-item__info > .product-title--inline > a").get_attribute("href")
        #print(f"IMAGE: {image_link}\n")
        with open (f"scraped_jeans/{n} {page}.jpg", "wb") as file:
            r = requests.get(image_link, allow_redirects=True)
            file.write(r.content)
        n = n + 1
    return n

def iterate_lowest_category(start_url):
    #SET MAXIMUM OF PAGES TO LOAD (EACH PAGE HAS MAXIMUM OF 24 PRODUCTS)
    counter = 1
    for n in range(1,3):
        driver.implicitly_wait(10)
        driver.get(start_url + f"?page={n}&view=list")
        driver.implicitly_wait(0)
        #TRY INCASE PAGE DOES NOT EXIST (OUT OF RANGE), OR PAGE SETUP IS DIFFERENT (CLOTHING FOR EXAMPLE HAS DIFFERENT SETUP)
        counter = scrape_page_layout_one(counter) #TODO: REMOVE N FROM FUNCTION (ONLY NEEDED FOR DEBUGGING)
        continue

if __name__ == '__main__':
    base_url = "https://www.bol.com"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    
    #driver.implicitly_wait(10)
    driver.maximize_window()
    driver.get(base_url)
    #ACCEPT COOKIES
    driver.find_element(By.CSS_SELECTOR, "wsp-consent-modal > div > button").click()
    #get_list()
    #get_one()
    #print("GETTING ALL SUB-CATEGORY URLS")
    #find_lowest_categories("https://www.bol.com/nl/nl/l/boeken/8299/")



iterate_lowest_category("https://www.bol.com/nl/nl/l/heren-jeans/47416/")