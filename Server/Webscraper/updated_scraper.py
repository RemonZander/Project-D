import os
import time

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from exif_data import ExifData
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

        self.image_download_failed = 0

        try:
            self.driver: Chrome = webdriver.Chrome(service=ChromeService(os.path.realpath("./driver/chromedriver.exe")), options=self.chrome_options)
        except Exception as e:
            print(e)

        self.logs = []

        self.directory = ""

        self.actual_total_amount = 0

        self.webdriver_wait = WebDriverWait(self.driver, 10)
        self.__initiate_scraper()

        self.driver.implicitly_wait(10)

        self.current_url = ""

        self.image_index = 1

        self.screen_blocked_amount = 0

    def scrape_starting_from_sub_menus(self, sub_menu_list):
        self.__initiate_scraper()

        sub_cats = self.__extract_sub_categories(sub_menu_list)

        for main_sub_cat in sub_cats:
            self.__scrape_lowest_categories(main_sub_cat, 20)
        self.__terminate_scraper()

    def scrape_lowest_categories_and_save_in_same_folder(self, category_list, folder_name, total_amount):
        amount_categories = len(category_list)
        amount_per_cat = -(total_amount // -amount_categories)
        actual_total_amount = amount_categories * amount_per_cat

        self.directory = folder_name

        self.actual_total_amount = actual_total_amount

        print("\nCLASSNAME OF CATEGORY: {}\nTOTAL AMOUNT: {}\nAMOUNT OF CATEGORIES: {}\nAMOUNT OF IMAGES SCRAPED PER CATEGORY: {}\nAMOUNT AFTER CALC: {}\n".format(
            folder_name,
            total_amount,
            amount_categories,
            amount_per_cat,
            actual_total_amount
        ))

        for cat in category_list:
            self.__iterate_lowest_category(cat, folder_name, amount_per_cat)

    def __initiate_scraper(self):
        self.driver.maximize_window()
        self.driver.get(self.base_url)

        # accept cookies
        try:
            self.driver.find_element(By.CSS_SELECTOR, "wsp-consent-modal > div > button").click()
        except Exception as e:
            pass

    def __terminate_scraper(self):
        self.driver.close()

    def __get_el_by_css_selector(self, selector: str, parent_element=None):
        if parent_element is not None:
            element: WebElement = self.webdriver_wait.until(EC.visibility_of(parent_element))

            return element.find_element(By.CSS_SELECTOR, selector)
        else:
            try:
                return self.webdriver_wait.until((EC.visibility_of_element_located((By.CSS_SELECTOR, selector))))
            except Exception as e:
                print("TIMEOUT EXCEPTION: ELEMENT WITH SELECTOR {} NOT FOUND IN CATEGORY {}\nURL: {}".format(selector, self.directory, self.current_url))

    def __get_els_by_css_selector(self, selector: str, parent_element=None):
        if parent_element is not None:
            element: WebElement = self.webdriver_wait.until(EC.visibility_of(parent_element))

            return element.find_elements(By.CSS_SELECTOR, selector)
        else:
            try:
                return self.webdriver_wait.until((EC.visibility_of_all_elements_located((By.CSS_SELECTOR, selector))))
            except Exception as e:
                print("TIMEOUT EXCEPTION: ELEMENTS WITH SELECTOR {} NOT FOUND IN CATEGORY {}\nURL: {}".format(selector, self.directory, self.current_url))

                # raise Exception("TIMEOUT EXCEPTION: ELEMENTS WITH SELECTOR {} NOT FOUND IN CATEGORY {}\nURL: {}".format(selector, self.directory, self.current_url)) from None

    """
    TODO: Turn some (or all) find_element statements into waits
    """
    def __get_item_properties(self, current_url, product: WebElement) -> tuple[str, ...]:
        product_link: str = "LINK NOT FOUND"
        product_name: str = "NAME NOT FOUND"
        image_link: str = "IMAGE NOT FOUND"
        product_description: str = "DESCRIPTION NOT FOUND"
        product_categories: list[str] = ["DESCRIPTION NOT FOUND"]
        product_size_specs: list[str] = ["SPECS NOT FOUND"]

        self.current_url = current_url

        try:
            self.webdriver_wait.until(EC.url_to_be(current_url))

            product_link: str = self.__get_el_by_css_selector("a.product-title", product).get_attribute("href")
            product_name: str = self.__get_el_by_css_selector("a.product-title", product).text

            self.driver.get(product_link)

            self.webdriver_wait.until(EC.url_to_be(product_link))

            image_link: str = self.__get_el_by_css_selector("div.image-slot > img").get_attribute("src")

            product_description: str = self.__get_el_by_css_selector("div.product-description").text

            product_specs = self.__get_el_by_css_selector("div[data-test='specifications']")

            product_categories: list[str] = list(
                map(lambda el: el.get_attribute("title"),
                    self.__get_els_by_css_selector("ul.specs__categories > li.specs__category > a", product_specs))
            )

            product_size_specs: list[str] = list(
                map(lambda el: el.text if "Maat & Pasvorm" in el.text else "",
                    self.__get_els_by_css_selector("div.specs:first-child", product_specs))
            )

        except Exception as e:
            print("CURRENT URL: {}".format(current_url))
            print(e)

            # self.logs.append("CURRENT URL: {}\nEXCEPTION MESSAGE: {}\n".format(current_url, str(e)))
        finally:
            self.driver.get(current_url)

            return product_name, image_link, product_link, product_description + "\n\n" + ",".join(product_size_specs), ",".join(product_categories)

    """
    Function that scrapes a page by recursively going on every product and getting the right properties.
    """
    def __scrape_page(self, current_url, n, max_items, directory):
        products_amount = len(self.__get_els_by_css_selector("li.product-item--row"))

        i = 0

        while i < products_amount:
            if n >= max_items:
                break

            print("CLASS: {}".format(directory))
            print("AMOUNT PRODUCTS: " + str(products_amount))
            print("MAX ITEMS = " + str(max_items))
            print("N = " + str(n))

            if path.exists(f"{directory}/{self.image_index}.jpg"):
                print("IMAGE ALREADY EXISTS... SKIPPING")
                n = n + 1
                i = i + 1
                self.image_index = self.image_index + 1
                continue

            product_element = self.__get_el_by_css_selector("ul.product-list > li:nth-child({})".format(i + 1))

            time.sleep(1)

            item_properties = self.__get_item_properties(current_url, product_element)

            if self.download_bool and item_properties[1] != "IMAGE NOT FOUND":
                try:
                    path_file = f"{directory}/{self.image_index}.jpg"

                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}

                    r = requests.get(item_properties[1], headers=headers, allow_redirects=True)

                    with open(path_file, "wb") as file_img:
                        file_img.write(r.content)

                    square_image(path_file)
                    ExifData(path_file).SaveData(item_properties[0], item_properties[4], item_properties[3])

                    self.image_index = self.image_index + 1
                except Exception as e:
                    print("ERROR DOWNLOADING IMAGE:")
                    print(e)
                    print("\n")

                    self.image_download_failed = self.image_download_failed + 1

            n = n + 1
            i = i + 1

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

            new_items = self.__scrape_page(current_url, current_items, max_items, directory)
            
            if new_items > current_items:
                page_num += 1
                current_items = current_items + new_items;
            elif new_items == current_items:
                self.driver.refresh()
                print("PAGE REFRESHED, CONTINUEING")
            else:
                print("Somehow new items is lower than current item?????")


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
    first_counter = time.perf_counter()

    bol_web_scraper = BolWebScraper(True)
    bol_web_scraper.scrape_lowest_categories_and_save_in_same_folder(categories, folder_name, amount)

    second_counter = time.perf_counter()

    return folder_name, bol_web_scraper.image_download_failed, second_counter - first_counter, bol_web_scraper.actual_total_amount, bol_web_scraper.screen_blocked_amount


if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/lange-jeans/47200/4295688522/",
                                          "https://www.bol.com/nl/nl/l/lange-broeken/47205/4295688522/",
                                          "https://www.bol.com/nl/nl/l/lange-broeken-jeans/46560/4295688522/",
                                          "https://www.bol.com/nl/nl/l/lange-broeken-jeans/46401/4295688522/",
                                          "https://www.bol.com/nl/nl/l/lange-broeken/47425/4295688522/",
                                          "https://www.bol.com/nl/nl/l/lange-jeans/47416/4295688522/"], "lange broeken", 10000),

           executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/heren-sneakers/37547/",
                                         "https://www.bol.com/nl/nl/l/dames-sneakers/37531/",
                                         "https://www.bol.com/nl/nl/l/meisjes-sneakers/46442/",
                                         "https://www.bol.com/nl/nl/l/sneakers-jongens/46589/"], "sneakers", 10000),

           executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/slippers-jongens/46600/",
                                         "https://www.bol.com/nl/nl/l/slippers-meisjes/46446/",
                                         "https://www.bol.com/nl/nl/l/heren-slippers/37549/",
                                         "https://www.bol.com/nl/nl/l/dames-slippers/37534/"], "slippers", 10000),

           # executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/jassen-dames/47203/",
           #                               "https://www.bol.com/nl/nl/l/jassen/47445/",
           #                               "https://www.bol.com/nl/nl/l/meisjes-jassen/46383/",
           #                               "https://www.bol.com/nl/nl/l/jongensjassen/46545/"], "jassen", 10000),

           # executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/jongensshirts/46556/",
           #                               "https://www.bol.com/nl/nl/l/t-shirts-meisjes/46394/",
           #                               "https://www.bol.com/nl/nl/l/shirts-heren/47412/",
           #                               "https://www.bol.com/nl/nl/l/t-shirts-dames/47302/"], "t-shirts", 10000),

           executor.submit(scrape_cats, ["https://www.bol.com/nl/nl/l/korte-broeken-jongens/46563/",
                                         "https://www.bol.com/nl/nl/l/korte-broeken-meisjes/46404/",
                                         "https://www.bol.com/nl/nl/l/korte-broeken-heren/47427/",
                                         "https://www.bol.com/nl/nl/l/korte-broeken-dames/47275/"], "korte broeken", 10000)
        ]

        results = concurrent.futures.wait(futures)

        print("DONE SCRAPING")
        with open("webscraper_log.txt", "w") as file:
            for future in results[0]:
                file.write("CLASS: {}\nIMAGES DOWNLOAD FAILED: {}\nTIME SPEND SCRAPING: {} minutes\nEXPECT TOTAL IMAGES: {}\nACTUAL TOTAL IMAGES: {}\nAMOUNT IP BLOCKED: {}\n\nLOGS:\WIP\n\n".format(
                    future.result()[0],
                    future.result()[1],
                    future.result()[2] / 60,
                    future.result()[3],
                    len(os.listdir(future.result()[0])),
                    future.result()[4]
                ))
