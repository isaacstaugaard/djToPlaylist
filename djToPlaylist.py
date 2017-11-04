# -*- coding: utf-8 -*-
import argparse 
import google.oauth2.credentials
import google_auth_oauthlib.flow	
import httplib2	
import os	
import psycopg2		
import smtplib	
import sys	
import time
import unicodedata
import urllib.request	
import urllib.error
from apiclient.discovery import build
from apiclient.errors import HttpError	
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow									 			  
from lxml import html 
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from selenium import webdriver
from selenium.webdriver.common.by import By                       
from selenium.webdriver.support.ui import WebDriverWait			 
from selenium.webdriver.common.keys import Keys                   
from selenium.webdriver.common.action_chains import ActionChains  
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.chrome.options import Options

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "../client_secret.json"
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
DEVELOPER_KEY = 'AIzaSyDOPvTdX7H5tVlmR6CP-L07hjD0I2gB-ts'
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'



def init_driver():
	chrome_options = Options()
	chrome_options.add_argument("user-data-dir=C:/Users/GAMER1/AppData/Local/Google/Chrome/User Data/Default");
	chrome_options.add_argument("--start-maximized");
	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.wait = WebDriverWait(driver, 5)
	return driver



def lookup(driver, query):
	venueAndDate = tracklistsSite(driver,query)
	time.sleep(3)
	linkDescription = getLink(driver,query)
	time.sleep(3)
	getDataAndMakePlaylist(driver, venueAndDate, linkDescription, query)
	time.sleep(4)



def tracklistsSite(driver,query):
	driver.get("https://www.1001tracklists.com/")
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
		time.sleep(3)

		#Click on the 1st menu item (usually closes the Most Liked 2017 Tab)
		side = driver.find_elements_by_xpath("//*[@id='leftContent']/div")
		side = side[-1]
		mlElem = side.find_element_by_xpath("div[1]/a[1]")
		mlElem.click()
		time.sleep(1)

		#Click on the second to last menu item (the Most Viewed Tracklists Ever tab)
		mvElem = side.find_elements_by_xpath("div[1]/a")
		mvElem[-2].click()
		time.sleep(1)

		#Click on the first link from the Most Viewed Tracklists Ever tab
		mvteElem = side.find_elements_by_xpath("div[1]/div")
		mvteElem = mvteElem[-2]
		mvteElem.find_element_by_xpath("table/tbody/tr/td/div/a").click()
		time.sleep(1)

		# Get the date and venue of the set
		elementChild  = driver.find_element_by_xpath("//*[contains(text(), 'TL date')]")
		element = elementChild.find_element_by_xpath('../following-sibling::td')
		date = element.text
		print("DATE: ", date, "\n")

		element = driver.find_elements_by_class_name('sideTop')[-1]
		element = element.find_element_by_xpath('tbody/tr/th')
		venue = element.text
		print("VENUE: ", venue, "\n")

		venuedate = []
		venuedate.append(venue)
		venuedate.append(date)
		return venuedate

	except TimeoutException:
		print("Could not process your request")



def getLink(driver,query):
	#Get the link to the set (soundcloud,mixcloud or other)
	link = "No soundcloud or mixcloud link"
	try: 
		element = driver.find_element_by_xpath("//*[@id='mediaItems']/div/ul/li[.//*[contains(.,'SoundCloud')]]")
	except: 
		try: 
			element = driver.find_element_by_xpath("//*[@id='mediaItems']/div/ul/li[.//*[contains(.,'MixCloud')]]")
		except: 
			print("No valid link")
	element.click()
	time.sleep(2)

	#Change frames and retrieve the link
	try: 
		driver.switch_to_frame(driver.find_element_by_class_name('scWidget1'))
		time.sleep(2)
		element = driver.find_element_by_xpath("//*[@id='widget']/div[3]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/a")
		link = element.get_attribute('href')
		print("LINK: ", link, "\n")
		return link
	except:
		try: 
			driver.switch_to_frame(driver.find_element_by_class_name('mcWidget1'))
			time.sleep(2)
			element = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/a")
			link = element.get_attribute('href')
			print("LINK: ", link, "\n")
			return link
		except:
			print("Could not change frames and retrieve link")
	return link



def getDataAndMakePlaylist(driver, venuedate, link, query):
	artists = []
	songs = []
	playlistName = "Songs from " + query + "'s set at " + venuedate[0] + ' on ' + venuedate[1] 

	#Creates a new playlist
	youtube = get_authenticated_service()
	plName = playlists_list_mine(youtube, part='snippet,contentDetails', mine=True, maxResults=25, onBehalfOfContentOwner='', onBehalfOfContentOwnerChannel='')
	for elem1 in plName:
		if(playlistName == elem1):
			print("There is already a playlist with this name. Exiting \n")
			return

	try:
		playlistID = add_playlist(youtube, playlistName, link, args)
	except urllib.error.HTTPError as e:
		print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
	driver.switch_to.default_content()

	#Loop through the songs from the set --> add song/artist to respective list --> youtube API to search for videoID --> add video to playlist
	for elem in driver.find_elements_by_xpath("//*[@itemprop='tracks']"):
		elemList = elem.find_elements_by_tag_name("meta")
		toSplit = elemList[0].get_attribute("content")
		splitList = toSplit.split(" - ")
		query = splitList[0] + ' ' + splitList[1]
		artists.append(splitList[0])
		songs.append(splitList[1])
		#Search on youtube for the video
		videoID = youtube_search(query, 10)
		#If there is no video for the song, skip it
		if not videoID:
			continue
		#Appends item to the playlist
		playlist_items_insert(youtube,{'snippet.playlistId': playlistID,'snippet.resourceId.kind': 'youtube#video','snippet.resourceId.videoId': videoID[0] ,'snippet.position': ''}, part='snippet',onBehalfOfContentOwner='')
	sizeOfPlaylist = len(artists)



def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)



def add_playlist(youtube, playlistName, link, args):
	body = dict(snippet=dict(title=playlistName, description=link),status=dict(privacyStatus='private'))
	#body = dict(snippet=dict(title=args.DJ, description=args.description),status=dict(privacyStatus='private')) 
	playlists_insert_response = youtube.playlists().insert(part='snippet,status',body=body).execute()
	print ('New playlist ID: %s' % playlists_insert_response['id'])
	return playlists_insert_response['id']



def print_response(response):
	print(response)	



# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]
      # For properties that have array values, convert a name like
      # "snippet.tags[]" to snippet.tags, and set a flag to handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True
      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource



# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.items():
      if value:
        good_kwargs[key] = value
  return good_kwargs



def playlist_items_insert(client, properties, **kwargs):
  resource = build_resource(properties)
  kwargs = remove_empty_kwargs(**kwargs)
  response = client.playlistItems().insert(
    body=resource,
    **kwargs
  ).execute()
  #return print_response(response)



def youtube_search(query, maxNum):
  youtube = build(API_SERVICE_NAME, API_VERSION,
    developerKey=DEVELOPER_KEY)
  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=query,
    part='id,snippet',
    maxResults=10
  ).execute()
  videos = []
  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videos.append('%s' % (search_result['id']['videoId']))
      break;
    elif search_result['id']['kind'] == 'youtube#channel':
    	continue;
    elif search_result['id']['kind'] == 'youtube#playlist':
    	continue;
  #print ('Videos:\n', videos[0])
  return (videos)



 # Sample python code for playlists.list
def playlists_list_mine(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)
  response = client.playlists().list(
    **kwargs
  ).execute()
  playlistTitles = []
  for item in response['items']:
    playlistTitles.append((item['snippet']['title']))
  return (playlistTitles)
  #return print_response(response)



if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("DJ",help = 'DJ Name')
	#argparser.add_argument('--description',
	#  default='All the songs from the setlist',
	#  help='The description of the new playlist.')
	driver = init_driver()
	args = argparser.parse_args()
	DJ = args.DJ
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	lookup(driver, DJ)
	driver.quit()