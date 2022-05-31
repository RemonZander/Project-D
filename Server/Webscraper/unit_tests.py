import unittest
from updated_scraper import BolWebScraper
import time

class TestBolScraper(unittest.TestCase):

    def setUp(self):
        self.bol_scraper = BolWebScraper(False)
        self.bol_scraper._BolWebScraper__initiate_scraper()

    ###Verify list of sub sub categories is > 0
    def test_extract_sub_categories(self):
        self.extract_sub_categories_computer_en_elektronica()
        self.extract_sub_categories_speelgoed_hobby_en_feest()
        self.extract_sub_categories_zwanger_baby_en_peuter()
        self.extract_sub_categories_mooi_en_gezond()
        self.extract_sub_categories_kleding_schoenen_en_accessoires()

    def extract_sub_categories_computer_en_elektronica(self):
        categories= ["https://www.bol.com/nl/nl/menu/categories/subMenu/3"]
        test = self.bol_scraper._BolWebScraper__extract_sub_categories(categories)
        self.assertGreater(len(test), 0)

    def extract_sub_categories_speelgoed_hobby_en_feest(self):
        category= ["https://www.bol.com/nl/nl/menu/categories/subMenu/4"]
        test = self.bol_scraper._BolWebScraper__extract_sub_categories(category)
        self.assertGreater(len(test), 0)

    def extract_sub_categories_zwanger_baby_en_peuter(self):
        category= ["https://www.bol.com/nl/nl/menu/categories/subMenu/5"]
        test = self.bol_scraper._BolWebScraper__extract_sub_categories(category)
        self.assertGreater(len(test), 0)

    def extract_sub_categories_mooi_en_gezond(self):
        category= ["https://www.bol.com/nl/nl/menu/categories/subMenu/6"]
        test = self.bol_scraper._BolWebScraper__extract_sub_categories(category)
        self.assertGreater(len(test), 0)

    def extract_sub_categories_kleding_schoenen_en_accessoires(self):
        category= ["https://www.bol.com/nl/nl/menu/categories/subMenu/7"]
        test = self.bol_scraper._BolWebScraper__extract_sub_categories(category)
        self.assertGreater(len(test), 0)

    #Attempt to scrape multiple items from sub category test_computer_en_elektronica
    #def test_computer_en_elektronica_1(self):
        #self.bol_scraper.__find_lowest_categories("https://www.bol.com/nl/nl/menu/categories/subMenu/3", 1)

    #def test_computer_en_elektronica_100(self):
        #self.bol_scraper.__find_lowest_categories("https://www.bol.com/nl/nl/menu/categories/subMenu/3", 100)

    #def test_kleding_schoenen_en_accessoires(self):
        #self.bol_scraper.__find_lowest_categories("https://www.bol.com/nl/nl/menu/categories/subMenu/7")

    def tearDown(self):
        self.bol_scraper._BolWebScraper__terminate_scraper()

if __name__ == '__main__':
    unittest.main()

var =   [
            "https://www.bol.com/nl/nl/menu/categories/subMenu/3",  #Computer en Elekronica
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/4",  #Speelgoed, Hobby en Feest
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/5",  #Zwanger, Baby & Peuter
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/6",  #Mooi & Gezond
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/7"  #Kleding, Schoenen & Accessoires
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/8",  #Sport, Outdoor & Reizen
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/12", #Kantoor & School
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/11", #Wonen, Koken & Huishouden
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/9",  #Dier, Tuin & Klussen
            #"https://www.bol.com/nl/nl/menu/categories/subMenu/13"  #Auto & Motor
        ]