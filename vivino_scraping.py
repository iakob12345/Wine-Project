from selenium import webdriver
import csv
import pandas as pd
from wine_links import all_links
from urllib.request import Request,urlopen
import time
from random import randint


class ChromeVivinoScraper:
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')

	def __init__(self, chrome_path, output_name, columns):
		self.chrome_path = chrome_path		
		self.output_name = output_name
		self.columns = columns
		self.driver = webdriver.Chrome(chrome_path, chrome_options = ChromeVivinoScraper.chrome_options)

	def __str__(self):
		return f"This scraper will output {self.output_name} file with the following fields: {self.columns}. "

	def open_files(self):
		with open(self.output_name,'w', encoding = "utf-8") as file:
			file.write(self.columns)

	def vivino_crawler(self):
		index_counter = 0
		dataset = []
		for name, link in all_links.items():
			#driver will crawl to each page
			self.driver.get(link)
			index_counter += 1
			#since pages are quite granular, it was determined that 40 times of page scrolling were enough getting the most amount of data
			for x in range(40):
				self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				#in order to make it seemless as possible, we emulate human-like behavior with random waiting times per scroll
				time.sleep(randint(1,5))
				#first we will crawl to all catalogs and then loop inside for each catalog
				total_catalog = self.driver.find_elements_by_class_name('explorerCard__titleColumn--28kWX')
				index_counter += 1
			for single_catalog in total_catalog:
				#since not all catalogs contain all the information, we will use try/except to still catch catalogs with some information in it
				try:
					wineries = single_catalog.find_element_by_class_name('vintageTitle__winery--2YoIr').text
					wine_names = single_catalog.find_element_by_class_name("vintageTitle__wine--U7t9G").text
				except:
					wineries = ''
					wine_names = ''
				try:
					countries = single_catalog.find_element_by_xpath(".//div[@class='vintageLocation__vintageLocation--1DF0p'][a]/a[2]").text if True else ''
					regions = single_catalog.find_element_by_xpath(".//div[@class='vintageLocation__vintageLocation--1DF0p'][a]/a[3]").text if True else ''
				except:
					countries = ''
					wine_names = ''
				try:
					link_wines = single_catalog.find_element_by_xpath(".//a[@class='anchor__anchor--2QZvA']").get_attribute('href') if True else ''
				except:
					link_wines = ''
				try:
					prices = single_catalog.find_element_by_xpath(".//div[@class='explorerCard__ratingAndPrice--2dw-T']/button/span").text[1:] 
				except:
					#to get a price information of a bottle, sometimes it is required to open a catalog page in itself and fetch data there, which in itself is a multi-step process
					try:
						self.driver.execute_script("window.open('');")
						self.driver.switch_to.window(self.driver.window_handles[1])
						self.driver.get(link_wines)
						prices = self.driver.find_element_by_class_name("purchaseAvailability__currentPrice--3mO4u").text[1:]
						time.sleep(randint(1,5))
					except Exception as e:
						try:
							prices_long = self.driver.find_element_by_class_name("purchaseAvailabilityPPC__notSoldContent--1yZZ0").text
							prices = prices_long[prices_long.find("€")+1:].split()[0]
							time.sleep(randint(1,5))
							print(e)
						except Exception as e:
							print(e)
							prices = ''
					finally:
						#closing an individual wine page and returning to the general catalog page
						self.driver.close()
						self.driver.switch_to.window(self.driver.window_handles[0])
				try:
					rating_avgs = single_catalog.find_element_by_class_name("vivinoRatingWide__averageValue--1zL_5").text if True else ''
					total_reviews = single_catalog.find_element_by_class_name("vivinoRatingWide__basedOn--s6y0t").text.split(" ")[0] if True else ''
				except:
					rating_avgs = ''
					total_reviews = ''

				index_counter += 1
				wine_dictionary = {
				'catalog': name,
				'wineries': wineries,
				'wine_names': wine_names,
				'countries': countries,
				'regions': regions,
				'prices': prices,
				'rating_avgs': rating_avgs,
				'total_reviews': total_reviews,
				'link_wines': link_wines
				}

				dataset.append(wine_dictionary)
				print(str(index_counter) + ":   " + name + "___" + wineries + wine_names + "___" + countries + "___" + regions + rating_avgs + "___" + total_reviews + "___" + link_wines+ '___' + prices )
				df = pd.DataFrame(dataset)
				df.to_csv(self.output_name, index=False)

		self.driver.close()


output_name = 'scraped_raw.csv'
chrome_path_mac = r"/Users/iakobkvataschidze/Desktop/Wine Project/chromedriver"
scraped_columns = 'winery, wine_name, country, region, price, rating, n_review, link \n'


vivino_scraper = ChromeVivinoScraper(output_name = output_name,  chrome_path = chrome_path_mac, columns = scraped_columns)
vivino_scraper.open_files()
vivino_scraper.vivino_crawler()

