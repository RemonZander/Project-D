from email.mime import image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def scrape_page_layout_one(n):
    #GET LIST OF ALL ITEMS
    items = driver.find_elements(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product)")
    print(f"length: {len(items)}")
    print(f"page: {n}")
    for item in items:
        #RETRIEVE NAME
        name = item.find_element(By.CSS_SELECTOR, ".product-item__content > .product-item__info > .product-title--inline").text
        #TRY-BLOCK FOR INCONSISTENCY PRODUCT IMAGES PLACEMENT IN WEBELEMENT
        try:
            image_link = item.find_element(By.CSS_SELECTOR, ".product-item__image > div > a > img").get_attribute("src")
        except:
            image_link = item.find_element(By.CSS_SELECTOR, ".product-item__image > div > a > .skeleton-image > div > img").get_attribute("src")

        #TODO: BOTH LINK AND NAME CAN BE FOUND IN SAME CLASSES, CAN IMPROVE THIS FOR CLARITY
        product_link = item.find_element(By.CSS_SELECTOR, ".product-item__content > .product-item__info > .product-title--inline > a").get_attribute("href")
        print(f"NAME: {name}\nIMAGE: {image_link}\nPRODUCT: {product_link}\n")

def scrape_page_layout_two(n):
    items = driver.find_elements(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product)")
    print(f"length: {len(items)}")
    print(f"page: {n}")
    for item in items:
        #RETRIEVE NAME
        name = item.find_element(By.CSS_SELECTOR, ".product-item__content > a > span").text
        #TRY-BLOCK FOR INCONSISTENCY PRODUCT IMAGES PLACEMENT IN WEBELEMENT
        try:
            image_link = item.find_element(By.CSS_SELECTOR, ".product-item__image > a > img").get_attribute("src")
        except:
            image_link = item.find_element(By.CSS_SELECTOR, ".product-item__image > a > .skeleton-image > .skeleton-image__container > img")
            if image_link.get_attribute("src") is None:
                print("CANNOT FIND SRC IN ELEMENT, TRYING ALTERNATIVE")
                #for attr in range(len(image_link.get_property("attributes"))):
                    #print(f"INDEX: {attr},\n {image_link.get_property('attributes')[attr]}\n\n")
                image_link = image_link.get_property("attributes")[1]["value"]
                print("FOUND IMAGE LINK" + image_link)
        product_link = item.find_element(By.CSS_SELECTOR, ".product-item__content > a").get_attribute("href")
        print(f"NAME: {name}\nIMAGE: {image_link}\nPRODUCT: {product_link}\n")

def iterate_lowest_category(start_url):
    #SET MAXIMUM OF PAGES TO LOAD (EACH PAGE HAS MAXIMUM OF 24 PRODUCTS)
    for n in range(1,200):
        driver.get(start_url + f"?page={n}")
        #TRY INCASE PAGE DOES NOT EXIST (OUT OF RANGE), OR PAGE SETUP IS DIFFERENT (CLOTHING FOR EXAMPLE HAS DIFFERENT SETUP)
        try:
            scrape_page_layout_one(n) #TODO: REMOVE N FROM FUNCTION (ONLY NEEDED FOR DEBUGGING)        
        except:
            print("---PAGE LAYOUT ONE ERROR, TRYING LAYOUT 2!---")
            #TRY INCASE PAGE DOES NOT EXIST (OUT OF RANGE)
            try:
                scrape_page_layout_two(n)
            except:
                print("---PAGE LAYOUT 2 FAILED ---")
                break




if __name__ == '__main__':
    base_url = "https://www.bol.com"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    #driver.implicitly_wait(20)
    driver.maximize_window()
    driver.get(base_url)

    #ACCEPT COOKIES
    driver.find_element(By.CSS_SELECTOR, "wsp-consent-modal > div > button").click()
    #get_list()
    #get_one()
    #print("GETTING ALL SUB-CATEGORY URLS")
    #find_lowest_categories("https://www.bol.com/nl/nl/l/boeken/8299/")



iterate_lowest_category("https://www.bol.com/nl/nl/l/heren-jeans/47416/?view=list")