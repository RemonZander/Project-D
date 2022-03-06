from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests

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
    print(sub_category_url)

    driver.get(sub_category_url)
    with open ("scraped_book.png", "wb") as file:
        l = driver.find_element(By.CSS_SELECTOR, ".js_item_root:not(.js_sponsored_product) > div > div > a > img").get_attribute("src")
        #.product-image.product-image--list.px_list_page_product_click
        #".product-image.product-image--list.px_list_page_product_click > img"
        r = requests.get(l, allow_redirects=True)

        file.write(r.content)
        #file.write(l.)
    #driver.quit()


if __name__ == '__main__':
    base_url = "https://www.bol.com"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.implicitly_wait(15)
    driver.maximize_window()
    driver.get(base_url)

    #ACCEPT COOKIES
    driver.find_element(By.CSS_SELECTOR, "wsp-consent-modal > div > button").click()
    get_list()
    #get_one()
