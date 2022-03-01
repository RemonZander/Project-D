from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

if __name__ == '__main__':
    base_url = "https://www.bol.com"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.implicitly_wait(10)

    driver.get(base_url)

    categories = driver.find_elements(By.CSS_SELECTOR, "wsp-main-nav-item > a")

    category_urls = []

    for category in categories:
        url = category.get_attribute("href")

        if url is not None:
            category_urls.append(url)

    print(category_urls)
