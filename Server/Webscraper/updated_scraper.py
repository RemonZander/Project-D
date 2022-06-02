import threading

import selenium.webdriver.remote.webelement
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from exif_data import ExifData
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import requests
import concurrent.futures
from os import path, makedirs
from square_image import square_image
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BolWebScraper:
    def __init__(self, download_bool):
        self.download_bool = download_bool
        self.base_url = "https://www.bol.com"
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('headless')
        self.driver: Chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=self.chrome_options)
        self.webdriver_wait = WebDriverWait(self.driver, 10)
        self.__initiate_scraper()
        #self.driver.implicitly_wait(10)

    def scrape_starting_from_sub_menus(self, sub_menu_list):
        self.__initiate_scraper()

        sub_cats = self.__extract_sub_categories(sub_menu_list)

        for main_sub_cat in sub_cats:
            self.__scrape_lowest_categories(main_sub_cat, 20)
        self.__terminate_scraper()

    def scrape_lowest_categories_and_save_in_same_folder(self, category_list, folder_name, amount_per_cat):
        amount_categories = len(category_list)
        total_amount = amount_categories * amount_per_cat

        print("\nCLASSNAME OF CATEGORY: {}\nTOTAL AMOUNT: {}\nAMOUNT OF CATEGORIES: {}\nAMOUNT OF IMAGES SCRAPED PER CATEGORY: {}\n".format(
            folder_name,
            total_amount,
            amount_categories,
            amount_per_cat
        ))

        for cat in category_list:
            self.__iterate_lowest_category(cat, folder_name, amount_per_cat)

    def __initiate_scraper(self):
        self.driver.maximize_window()
        self.driver.get(self.base_url)

        # accept cookies
        try:
            self.driver.find_element(By.CSS_SELECTOR, "wsp-consent-modal > div > button").click()
        except :
            pass       

    def __terminate_scraper(self):
        self.driver.close()

    """
    TODO: Turn some (or all) find_element statements into waits
    """
    def __get_item_properties(self, current_url, product: WebElement) -> tuple[str, ...]:
        self.webdriver_wait.until(EC.url_to_be(current_url))

        product_element: WebElement = self.webdriver_wait.until(EC.visibility_of(product))

        product_link: str = product_element.find_element(By.CSS_SELECTOR, "a.product-title").get_attribute("href")
        product_name: str = product_element.find_element(By.CSS_SELECTOR, "a.product-title").text

        self.driver.get(product_link)

        self.webdriver_wait.until(EC.url_to_be(product_link))

        image_link: str = self.driver.find_element(By.CSS_SELECTOR, "div.image-slot > img").get_attribute("src")
        product_description = self.driver.find_element(By.CSS_SELECTOR, "div.product-description").text
        product_categories: list[str] = list(
            map(lambda el: el.get_attribute("title"),
                self.driver.find_elements(By.CSS_SELECTOR, "ul.specs__categories > li.specs__category > a"))
        )

        self.driver.get(current_url)

        return product_name, image_link, product_link, product_description, ",".join(product_categories)

    # def __get_image_link(self, product_id) -> str:
    #     image_link: str = 'li[data-id="{}"] img'.format(product_id)
    #
    #     try:
    #         image_link = self.webdriver_wait.until(EC.presence_of_element_located(
    #             (By.CSS_SELECTOR, 'li[data-id="{}"] img'.format(product_id)))).get_attribute("src")
    #     except TimeoutError:
    #         print("TIMEOUT ERROR")
    #     finally:
    #         return image_link

    def __get_product_description(self, product_link):
        self.driver.get(product_link)

        product_description = "NOT FOUND"

        try:
            product_description = self.driver.find_element(By.CSS_SELECTOR, "div.product-description").text
        except Exception:
            print("Description element not found.")

        self.driver.back()

        return product_description

    """
    Function that scrapes a page by recursively going on every product and getting the right properties.
    """
    def __scrape_page(self, current_url, n, max_items, directory):
        products = self.driver.find_elements(By.CSS_SELECTOR, "li.product-item--row")

        for i, product in enumerate(products):
            if n >= max_items:
                return n

            print("CLASS: {}".format(directory))
            print("AMOUNT PRODUCTS: " + str(len(products)))
            print("MAX ITEMS = " + str(max_items))
            print("N = " + str(n))

            product_element = self.driver.find_element(By.CSS_SELECTOR, "ul.product-list > li:nth-child({})".format(i + 1))
            product_id = product_element.get_attribute("data-id")
            item_properties = self.__get_item_properties(current_url, product_element)

            if self.download_bool:
                path_file = f"{directory}/{product_id}.jpg"

                with open(path_file, "wb") as file:
                    r = requests.get(item_properties[1], allow_redirects=True)
                    file.write(r.content)

                square_image(path_file)
                ExifData(path_file).SaveData(item_properties[0], item_properties[4], item_properties[3])
            n = n + 1
        return n

    def __iterate_lowest_category(self, start_url, directory, max_items) -> None:
        current_items = 0
        page_num = 1

        if not path.exists(directory) and self.download_bool:
            makedirs(directory)

        self.driver.get(start_url + f"?page={page_num}&view=list")
        pages_element = self.driver.find_element(By.CSS_SELECTOR, ".pagination")
        children = pages_element.find_elements(By.XPATH, "./*")

        if len(children) == 1:
            max_pages = children[0].find_element(By.CSS_SELECTOR, "span").text
        else:
            max_pages = children[-2].find_element(By.CSS_SELECTOR, ".js_pagination_item").get_attribute("data-page-number")

        while current_items < max_items and page_num <= int(max_pages):
            current_url = start_url + f"?page={page_num}&view=list"

            self.driver.get(current_url)

            current_items = self.__scrape_page(current_url, current_items, max_items, directory)

            page_num += 1

    def __scrape_lowest_categories(self, start_url, amount, path=""):
        # CHANGE DRIVER LOCATION TO URL
        self.driver.get(start_url)

        sub_categories = self.driver.find_elements(By.CSS_SELECTOR, ".facet-control__filter.facet-control__filter--no-padding > a")

        # NO MORE SUB-CATEGORIES? THEN START SCRAPING DATA (BASE CASE)
        if len(sub_categories) == 0:
            # TODO: Separate function needed for clarity and modularity
            print("\n\nURL: " + start_url)
            print("PATH: " + path)
            self.__iterate_lowest_category(start_url, start_url.split("/")[6], amount)
            return

        # Extract hrefs from categories
        extracted_url_list = []

        ##ALL CATEGORIES
        for sub_cat in sub_categories:
            extracted_url_list.append(sub_cat.get_attribute("href"))

        # Else call function with next sub-category url
        # For each sub-category -> find_lowest_categories(sub_category.url)
        for url in extracted_url_list:
            self.__scrape_lowest_categories(url, amount, f"{start_url}>{path}")  # Delimeter is ">"

    def __extract_sub_categories(self, main_category_urls):
        for cat_url in main_category_urls:
            self.driver.get(cat_url)
            main_sub_cat_list = self.driver.find_elements(By.CSS_SELECTOR, "main > div > div > ul > li > a")
            sub_cats = []
            for main_sub_cat in main_sub_cat_list:
                title = main_sub_cat.text
                if "alles" in title.lower() or "alle" in title.lower():
                    pass
                else:
                    sub_cats.append(main_sub_cat.get_attribute("href"))
            return sub_cats


# Function added for concurrency
def scrape_cats(categories, folder_name, amount):
    bol_web_scraper = BolWebScraper(True)
    bol_web_scraper.scrape_lowest_categories_and_save_in_same_folder(categories, folder_name, amount)


if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/lange-jeans/47200/4295688522/",
                                      "https://www.bol.com/nl/nl/l/lange-broeken/47205/4295688522/",
                                      "https://www.bol.com/nl/nl/l/lange-broeken-jeans/46560/4295688522/",
                                      "https://www.bol.com/nl/nl/l/lange-broeken-jeans/46401/4295688522/",
                                      "https://www.bol.com/nl/nl/l/lange-broeken/47425/4295688522/",
                                      "https://www.bol.com/nl/nl/l/lange-jeans/47416/4295688522/"], "lange broeken", 20)

        executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/heren-sneakers/37547/",
                                      "https://www.bol.com/nl/nl/l/dames-sneakers/37531/",
                                      "https://www.bol.com/nl/nl/l/meisjes-sneakers/46442/",
                                      "https://www.bol.com/nl/nl/l/sneakers-jongens/46589/"], "sneakers", 20)

        executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/slippers-jongens/46600/",
                                      "https://www.bol.com/nl/nl/l/slippers-meisjes/46446/",
                                      "https://www.bol.com/nl/nl/l/heren-slippers/37549/",
                                      "https://www.bol.com/nl/nl/l/dames-slippers/37534/"], "slippers", 20)

        executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/jassen-dames/47203/",
                                      "https://www.bol.com/nl/nl/l/jassen/47445/",
                                      "https://www.bol.com/nl/nl/l/meisjes-jassen/46383/",
                                      "https://www.bol.com/nl/nl/l/jongensjassen/46545/"], "jassen", 20)

        executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/jongensshirts/46556/",
                                      "https://www.bol.com/nl/nl/l/t-shirts-meisjes/46394/",
                                      "https://www.bol.com/nl/nl/l/shirts-heren/47412/",
                                      "https://www.bol.com/nl/nl/l/t-shirts-dames/47302/"], "t-shirts", 20)

        executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/korte-broeken-jongens/46563/",
                                      "https://www.bol.com/nl/nl/l/korte-broeken-meisjes/46404/",
                                      "https://www.bol.com/nl/nl/l/korte-broeken-heren/47427/",
                                      "https://www.bol.com/nl/nl/l/korte-broeken-dames/47275/"], "korte broeken", 20)
