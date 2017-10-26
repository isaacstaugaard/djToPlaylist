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


# Email for testing this program is t3std3v3lop3r123@gmail.com, password is t3std3v3lop3r #
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
		#------------------------------ FIX THIS: SOME ARTISTS DON't HAVE A SECTION FOR MOST LIKED TRACKS 2017. Retrieve the Most Viewed Ever from reverse -----------------------------#
		driver.find_element_by_xpath("//*[@id='leftContent']/div[2]/div[1]/a[4]").click()
		#Click on the first link 
		driver.find_element_by_xpath("//*[@id='leftContent']/div[2]/div[1]/div[4]/table/tbody/tr/td/div/a").click()
		
		# Get the date and venue of the set
		elementChild  = driver.find_element_by_xpath("//*[contains(text(), 'TL date')]")
		element = elementChild.find_element_by_xpath('../following-sibling::td')
		date = element.text
		print("DATE: ", date, "\n")
		element = driver.find_elements_by_class_name('sideTop')[-1]
		element = element.find_element_by_xpath('tbody/tr/th')
		venue = element.text
		print("VENUE: ", venue, "\n")
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

		#Change frames and retrieve the link
		try: 
			driver.switch_to_frame(driver.find_element_by_class_name('scWidget1'))
			element = driver.find_element_by_xpath("//*[@id='widget']/div[3]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/a")
			link = element.get_attribute('href')
			print("LINK: ", link, "\n")
		except:
			try: 
				driver.switch_to_frame(driver.find_element_by_class_name('mcWidget1'))
				element = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/a")
				link = element.get_attribute('href')
				print("LINK: ", link, "\n")
			except:
				print("Could not change frames and retrieve link")

		time.sleep(3)
		artists = []
		songs = []
		driver.switch_to.default_content()
		for elem in driver.find_elements_by_xpath("//*[@itemprop='tracks']"):
			elemList = elem.find_elements_by_tag_name("meta")
			toPrint = str(elemList[0].get_attribute("content").encode("utf-8"))[2:-1]
			splitList = toPrint.split(" - ")
			artists.append(splitList[0])
			songs.append(splitList[1])
			#Prints the artist/song line by line
			#print (toPrint.split(" - "))
		print("ARTISTS: ", artists, "\n")
		print("SONGS: ", songs, "\n")

		j = 0
		sizeOfPlaylist = len(artists)

		#Go to youtube.com

		###############################################################################################################################

		time.sleep(5)
		# while(j < sizeOfPlaylist):
		# 	driver.get("https://www.youtube.com/")
		# 	box = driver.wait.until(EC.presence_of_element_located(
		# 		(By.NAME, "search_query")))
		# 	button = driver.wait.until(EC.element_to_be_clickable(
		# 		(By.ID, "search-icon-legacy")))
		# 	box.send_keys(artists[j] + " " + songs[j])
		# 	try:
		# 		button.click()
		# 	except ElementNotVisibleException:
		# 		button = driver.wait.until(EC.visibility_of_element_located(
		# 			(By.NAME, "btnG")))
		# 		button.click()
		# 	time.sleep(3)
		# 	j+=1


	except TimeoutException:
		print("Could not process your request")

def lookupYT(driver,query):
		driver.get("https://www.youtube.com/")
		driver.maximize_window()
		time.sleep(3)
		try:
			# Sign in to youtube account
			signIn = driver.find_element_by_xpath("//*[@id='buttons']/ytd-button-renderer[2]/a")
			signIn.click()
			time.sleep(3)
			emailQuery = driver.find_element_by_xpath("//*[@id='identifierId']")
			emailQuery.send_keys("t3std3v3lop3r123@gmail.com")
			time.sleep(1)
			emailQuery.send_keys(Keys.ENTER)
			time.sleep(3)

			passQuery = driver.find_element_by_xpath("//*[@id='password']/div[1]/div/div[1]/input")
			passQuery.send_keys("t3std3v3lop3r")
			time.sleep(3)
			passQuery.send_keys(Keys.ENTER)
			time.sleep(5)
			
			# Go to user's channel
			accButton = driver.find_element_by_xpath("//*[@id='img']")
			accButton.click()
			time.sleep(3)
			accButton = driver.find_element_by_xpath("//*[@id='endpoint']/paper-item/div/yt-icon")
			accButton.click()
			time.sleep(5)

			# #Create a new playlist
			# button = driver.find_element_by_xpath("//*[@id='edit-buttons']/ytd-button-renderer[1]/a")
			# button.click()
			# time.sleep(3)
			# button = driver.find_element_by_xpath("//*[@id='channel-navigation-menu']/li[3]/a/span")
			# button.click()
			# time.sleep(3)
			# button = driver.find_element_by_xpath("//*[@id='playlists-tab-create-playlist-widget']/button")
			# button.click()
			# time.sleep(3)
			# playlistQuery = driver.find_element_by_xpath("//*[@id='playlists-tab-create-playlist-dialog']/form/div[1]/label/h2")
			# playlistQuery = playlistQuery.find_element_by_xpath('../span[1]/span[1]/input[1]')
			# playlistQuery.send_keys("Marshmello EDC")
			# time.sleep(3)
			# playlistQuery.send_keys(Keys.ENTER)

			#If already has playlist... 

			#Add songs to playlist 
			

		except:
			print("could not find the playlistquery")

if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("DJ",help = 'DJ Name')
	driver = init_driver()
	args = argparser.parse_args()
	DJ = args.DJ
	lookupYT(driver, DJ)
	#lookup(driver, DJ)
	#time.sleep(4)
	driver.quit()