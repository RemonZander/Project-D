import unittest
from updated_scraper import BolWebScraper
from updated_scraper import scrape_cats
from exif_data import ExifData
import os.path as path
import shutil


class TestBolScraper(unittest.TestCase):
    def setUp(self):
        self.enable_download = True

        self.scraper = BolWebScraper(self.enable_download)
        self.current_directory = path.dirname(path.abspath(__file__))

    def test_scrape_lowest_categories_and_save_in_same_folder(self):
        # Arrange / Act
        self.scraper.scrape_lowest_categories_and_save_in_same_folder(
            ["https://www.bol.com/nl/nl/l/lange-jeans/47200/4295688522/"],
            "lange broeken",
            1
        )

        # Assert
        self.result_directory = path.realpath(self.current_directory + "/lange broeken")
        self.result_image = path.realpath(self.result_directory + "/1.jpg")

        self.assertTrue(path.exists(self.result_directory))
        self.assertTrue(path.isfile(self.result_image))

        exif_data_obj = ExifData(self.result_image)

        self.assertIsNotNone(exif_data_obj.LoadData())

        # Cleanup
        shutil.rmtree(self.result_directory)

    def test_scrape_cats(self):
        # Arrange / Act
        data = scrape_cats(
            ["https://www.bol.com/nl/nl/l/lange-jeans/47200/4295688522/"],
            "lange broeken",
            1
        )

        # Assert
        self.assertEqual("lange broeken", data[0])
        self.assertEqual(0, data[1])
        self.assertTrue(isinstance(data[2], float))
        self.assertEqual(1, data[3])
        self.assertEqual(0, data[4])

    def tearDown(self):
        self.scraper.terminate_scraper()


if __name__ == '__main__':
    unittest.main()
