import time
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request
import argparse 												  #Needed to read the args from cmd line 
from lxml import html 
from selenium.webdriver.common.by import By                       #Allows the use of By 
from selenium.webdriver.support.ui import WebDriverWait			  #Allows for the driver to wait for dadta
from selenium.webdriver.common.keys import Keys                   #Allows for scrolling down (PGDOWN key)
from selenium.webdriver.common.action_chains import ActionChains  #Allows for mouseOver
import smtplib													  #Allows use of email
import psycopg2
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException

def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)
    return driver

def lookup(driver, query):
	driver.get("https://www.1001tracklists.com/")
	driver.maximize_window()
	try:
		#Find the search menu and change the value from tracklists to Djs
		searchmenu = driver.wait.until(EC.presence_of_element_located(
			(By.NAME, "search_selection")))
		searchmenu.click()
		time.sleep(.5)
		driver.find_element_by_xpath("//*[@id='search_selection']/option[3]").click()
		
		#Find the search bar and search for the DJ name given into this function
		box = driver.wait.until(EC.presence_of_element_located(
			(By.NAME, "main_search")))
		button = driver.wait.until(EC.element_to_be_clickable(
			(By.ID, "searchBtn")))
		box.send_keys(query)
		try:
			button.click()
		except ElementNotVisibleException:
			button = driver.wait.until(EC.visibility_of_element_located(
				(By.NAME, "btnG")))
			button.click()
		
		#Click on the artists link to go to his page
		try: 
			driver.find_element_by_xpath("//*[@id='middleTbl']/tbody/tr/td/table/tbody/tr[2]/td/div[1]/a").click()
		except:
			print("Artist not found")
		
		#Closes the cookies pop up
		driver.find_element_by_xpath("//*[@id='cookieMessage']/span").click()
		#Close the Most Liked Tracklists YEAR menu
		driver.find_element_by_xpath("//*[@id='leftContent']/div[2]/div[1]/a[1]").click()
		#Open the Most Viewed Tracklists Ever menu
		driver.find_element_by_xpath("//*[@id='leftContent']/div[2]/div[1]/a[4]").click()
		#Click on the first link 
		driver.find_element_by_xpath("//*[@id='leftContent']/div[2]/div[1]/div[4]/table/tbody/tr/td/div/a").click()
		
		# Get the date and venue of the set
		elementChild  = driver.find_element_by_xpath("//*[contains(text(), 'TL date')]")
		element = elementChild.find_element_by_xpath('../following-sibling::td')
		date = element.text
		print("DATE: ", date)
		element = driver.find_elements_by_class_name('sideTop')[-1]
		element = element.find_element_by_xpath('tbody/tr/th')
		venue = element.text
		print("VENUE: ", venue)
		link = ""
		#Get the link to the set (soundcloud,mixcloud or other)
		try: 
			element = driver.find_element_by_xpath("//*[@id='mediaItems']/div/ul/li[.//*[contains(.,'SoundCloud')]]")
		except: 
			try: 
				element = driver.find_element_by_xpath("//*[@id='mediaItems']/div/ul/li[.//*[contains(.,'MixCloud')]]")
			except: 
				print("No valid link")
		element.click()

		try: 
			driver.switch_to_frame(driver.find_element_by_class_name('scWidget1'))
			element = driver.find_element_by_xpath("//*[@id='widget']/div[3]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/a")
			link = element.get_attribute('href')
			print("ASDF: ", link)
			#driver.switchTo().defaultContent();
		except:
			try: 
				driver.switch_to_frame(driver.find_element_by_class_name('mcWidget1'))
				element = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/a")
				link = element.get_attribute('href')
				print("ASDF: ", link)
			except:
				print("Couldn't change frames")



	except TimeoutException:
		print("Box or Button not found on 1001tracklists.com")

if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("DJ",help = 'DJ Name')
	driver = init_driver()
	args = argparser.parse_args()
	DJ = args.DJ
	lookup(driver, DJ)
	time.sleep(4)
	driver.quit()