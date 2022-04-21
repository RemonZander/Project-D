from email.mime import image
from turtle import down
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import concurrent.futures
from os import path, makedirs

class BolWebScraper:
    def __init__(self, download_bool):
        self.download_bool = download_bool
        self.base_url = "https://www.bol.com"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.implicitly_wait(10)

    def scrape_starting_from_sub_menus(self, sub_menu_list):
        self.__initiate_scraper()
        #MAIN-CATEGORIES WE WANT TO SCRAPE (HARD CODED TO EXLUDE SPECIFIC CATEGORIES)
        sub_cats = self.__extract_sub_categories(sub_menu_list)
        for main_sub_cat in sub_cats:
            #print(title)
            #print(main_sub_cat.get_attribute("href"))
            self.__scrape_lowest_categories(main_sub_cat, 20)
        self.__terminate_scraper()

    def __initiate_scraper(self):
        self.driver.maximize_window()
        self.driver.get(self.base_url)
        #accept cookies
        self.driver.find_element(By.CSS_SELECTOR, "wsp-consent-modal > div > button").click()


    def __terminate_scraper(self):
        self.driver.close()

    # RETURNS TUPLE (product_name, product_image, product_link)
    def __get_item_properties(self, item):
        image_link = self.__get_image_link(item)
        product_link = item.find_element(By.CSS_SELECTOR, ".product-item__content > .product-item__info > .product-title--inline > a").get_attribute("href")
        product_name = item.find_element(By.CSS_SELECTOR, ".product-item__content > .product-item__info > .product-title--inline").text
        return (product_name, image_link, product_link)

    def __get_image_link(self, item):
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
        return image_link

    def __download_image(self, dir, n, image_link):
        with open (f"{dir}/{n}.jpg", "wb") as file:
            r = requests.get(image_link, allow_redirects=True)
            file.write(r.content)
            return True

    def __scrape_page(self, n, maxItems, dir):
        #GET LIST OF ALL ITEMS
        items = self.driver.find_elements(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product)")
        #print(f"length: {len(items)}")
        #print(f"page: {n}")
        #page = driver.find_element(By.CSS_SELECTOR, ".is-active > span").text 
        for item in items:
            if n >= maxItems:
                return n
            item_properties = self.__get_item_properties(item)
            if(self.download_bool):
                self.__download_image(dir, n, item_properties[1])
            n = n + 1
        return n

    def __iterate_lowest_category(self, start_url, maxItems):
        currentItems = 0
        pageNum = 1
        #GET DIR NAME FROM URL
        dir_name = start_url.split("/")[6]
        if not (path.exists(dir_name)):
            makedirs(dir_name)
        while currentItems < maxItems:
            self.driver.get(start_url + f"?page={pageNum}&view=list")
            #TRY INCASE PAGE DOES NOT EXIST (OUT OF RANGE), OR PAGE SETUP IS DIFFERENT (CLOTHING FOR EXAMPLE HAS DIFFERENT SETUP)
            currentItems = self.__scrape_page(currentItems, maxItems, dir_name) #TODO: REMOVE N FROM FUNCTION (ONLY NEEDED FOR DEBUGGING)
            pageNum += 1

    def __scrape_lowest_categories(self, start_url, amount, path=""):
        #CHANGE DRIVER LOCATION TO URL
        self.driver.get(start_url)

        #SEARCH FOR SUB-CATEGORIES ON PAGE
        sub_categories = self.driver.find_elements(By.CSS_SELECTOR, ".facet-control__filter.facet-control__filter--no-padding > a")

        #NO MORE SUB-CATEGORIES? THEN START SCRAPING DATA (BASE CASE)
        if len(sub_categories) == 0:
            #TODO: Separate function needed for clarity and modularity
            print("\n\nURL: " + start_url)
            print("PATH: "+ path)      
            self.__iterate_lowest_category(start_url, amount)
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
            self.__scrape_lowest_categories(url, f"{start_url}>{path}", amount) #Delimeter is ">"

    def __extract_sub_categories(self, main_category_urls):
        for cat_url in main_category_urls:
            self.driver.get(cat_url)
            main_sub_cat_list = self.driver.find_elements(By.CSS_SELECTOR, "main > div > div > ul > li > a")
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
            return sub_cats

if __name__ == '__main__':
    bol_web_scraper = BolWebScraper(True)
    bol_web_scraper.scrape([
            "https://www.bol.com/nl/nl/menu/categories/subMenu/3",  #Computer en Elekronica
            "https://www.bol.com/nl/nl/menu/categories/subMenu/4",  #Speelgoed, Hobby en Feest
            "https://www.bol.com/nl/nl/menu/categories/subMenu/5",  #Zwanger, Baby & Peuter
            "https://www.bol.com/nl/nl/menu/categories/subMenu/6",  #Mooi & Gezond
            "https://www.bol.com/nl/nl/menu/categories/subMenu/7",  #Kleding, Schoenen & Accessoires
            "https://www.bol.com/nl/nl/menu/categories/subMenu/8",  #Sport, Outdoor & Reizen
            "https://www.bol.com/nl/nl/menu/categories/subMenu/12", #Kantoor & School
            "https://www.bol.com/nl/nl/menu/categories/subMenu/11", #Wonen, Koken & Huishouden
            "https://www.bol.com/nl/nl/menu/categories/subMenu/9",  #Dier, Tuin & Klussen
            "https://www.bol.com/nl/nl/menu/categories/subMenu/13"  #Auto & Motor
        ])