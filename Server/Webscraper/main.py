from email.mime import image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import concurrent.futures


def get_list():
    categories = driver.find_elements(By.CSS_SELECTOR, "wsp-main-nav-category-ab > ul > li > a")
    #SPECIFIC
    #li[data-nav-id='1']
    #wsp-main-nav-item[data-name='category-menu']
    #"wsp-main-nav-item[data-name='category-menu'] > li > a"

    #ALL CATEGORIES (submenus)
    #"wsp-main-nav-category-ab > ul > li > a"

    #SPECIFIC CATEGORY (Filmstrip)
    #"wsp-filmstrip > div > ol > li > a"
    urls = []
    for category in categories:
        scraped_url = category.get_attribute("href")
        if scraped_url is not None:
            urls.append(scraped_url)

    for url in urls:
        print(f"MAIN CATEGORY: {url}")
        #Change to submenu screen
        driver.get(url)
        sub_categories = driver.find_elements(By.CSS_SELECTOR, "main > div > div > ul > li > a")
        print("SUB CATEGORIES")
        for sub_category in sub_categories:
            if sub_category is not None:
                print(f"\t{sub_category.get_attribute('href')}")
    #driver.quit()


def get_one():
    #FIND SUB-CATEGORY MENU LINK
    category = driver.find_element(By.CSS_SELECTOR, "wsp-main-nav-category-ab > ul > li > a")
    scraped_url = category.get_attribute("href")
    print(f"scraped_url = {scraped_url}")
    driver.get(scraped_url)

    sub_category = driver.find_element(By.CSS_SELECTOR, "main > div > div > ul > li > a")
    sub_category_url = sub_category.get_attribute("href")
    print(f"sub cat: {sub_category_url}")

    driver.get(sub_category_url)
    l = driver.find_element(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product) > .product-item__content > .product-item__info > .product-title--inline")
    #print(l)
    print(l.text)

    test = driver.find_element(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product)")
    a = test.find_element(By.CSS_SELECTOR, ".product-item__content > .product-item__info > .product-title--inline")
    print(a.text)

    #with open ("scraped_book.png", "wb") as file:
        #l = driver.find_element(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product) > div > div > a > img").get_attribute("src")
        #.product-image.product-image--list.px_list_page_product_click
        #".product-image.product-image--list.px_list_page_product_click > img"
        #r = requests.get(l, allow_redirects=True)

        #file.write(r.content)
    driver.quit()

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
    for n in range(1,3):
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

def find_lowest_categories(start_url, path=""):
    #CHANGE DRIVER LOCATION TO URL
    driver.get(start_url)

    #SEARCH FOR SUB-CATEGORIES ON PAGE
    sub_categories = driver.find_elements(By.CSS_SELECTOR, ".facet-control__filter.facet-control__filter--no-padding > a")

    #NO MORE SUB-CATEGORIES? THEN START SCRAPING DATA (BASE CASE)
    if len(sub_categories) == 0:
        #TODO: Separate function needed for clarity and modularity
        print("\n\nURL: " + start_url)
        print("PATH: "+ path)      
        iterate_lowest_category(start_url)
        return

    #Extract hrefs from categories
    extracted_url_list = []

    ##FOR LIMITED CATEGORIES RANGE
    #for i in range(1):
        #try: #We arent checking the range of the actual list, so if its shorter than the limit we just break out of the loop
            #extracted_url_list.append(sub_categories[i].get_attribute("href"))
        #except:
           #break

    ##ALL CATEGORIES
    for sub_cat in sub_categories:
        extracted_url_list.append(sub_cat.get_attribute("href"))

    #Else call function with next sub-category url
        #For each sub-category -> find_lowest_categories(sub_category.url)
    for url in extracted_url_list:
        find_lowest_categories(url, f"{start_url}>{path}") #Delimeter is ">"


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



    #MAIN-CATEGORIES WE WANT TO SCRAPE (HARD CODED TO EXLUDE SPECIFIC CATEGORIES)
    categories_urls = [
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/3",  #Computer en Elekronica
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/4",  #Speelgoed, Hobby en Feest
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/5",  #Zwanger, Baby & Peuter
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/6",  #Mooi & Gezond
        "https://www.bol.com/nl/nl/menu/categories/subMenu/7"  #Kleding, Schoenen & Accessoires
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/8",  #Sport, Outdoor & Reizen
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/12", #Kantoor & School
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/11", #Wonen, Koken & Huishouden
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/9",  #Dier, Tuin & Klussen
        #"https://www.bol.com/nl/nl/menu/categories/subMenu/13"  #Auto & Motor
    ]
    
    #TODO: MAKE SEPARATE FUNCTION
    for cat_url in categories_urls:
        driver.get(cat_url)
        main_sub_cat_list = driver.find_elements(By.CSS_SELECTOR, "main > div > div > ul > li > a")
        sub_cats = []
        for main_sub_cat in main_sub_cat_list:
            title = main_sub_cat.text
            #FILER ALLE AND ALLES (CATEGORIES CONTAINING ALL CATEGORIES)
            if "alles" in title.lower() or "alle" in title.lower():
                pass
            else:
                sub_cats.append(main_sub_cat.get_attribute("href"))

        #with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            #{executor.submit(find_lowest_categories, sc): sc for sc in sub_cats}


        for main_sub_cat in sub_cats:
            #print(title)
            #print(main_sub_cat.get_attribute("href"))
            find_lowest_categories(main_sub_cat)