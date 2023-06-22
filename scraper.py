########
"""
Krishna Panchap / Heretic
This module takes the unsplash query and returns a
filtered CSV containing URL of each image
"""
########
import time, csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dataclasses import dataclass

## CONSTANTS ##
URL = "https://unsplash.com/s/photos/living-room-interior-design?license=free"
AUTHORS_TO_EXCLUDE = ["spacejoy", "collovhome"]
TAGS_TO_EXCLUDE = {"bed", "bedroom", "bedrooms", "bedroom interior", "dining table", "dining room", "dining"}

## Class to store images and meta data ## 
@dataclass
class ImageItem:
    image_url: str
    author: str
    tags: list[str]

# create instance of browser
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.implicitly_wait(20) # gives an implicit wait for 20 seconds

driver.get(URL)
## note: assuming same counts of subclass elements
## output list ##
results = []

## click the "Load More" Button to show more results
loadMoreButton = driver.find_element(By.XPATH, "//button[@class='CwMIr DQBsa p1cWU jpBZ0 AYOsT Olora I0aPD dEcXu WMIal']")
time.sleep(2)
loadMoreButton.click()

lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
match=False
##### time out number which can be set to close runtime of search ###
# timeout = time.time() + 60*10   # 5 minutes from now
while (match==False):
#        if time.time() > timeout:
#            break
        lastCount = lenOfPage
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        time.sleep(2.5)
        lenOfPage = driver.execute_script("window.scrollBy(0,-300)")
        time.sleep(5)
        lenOfPage = driver.execute_script("window.scrollBy(0,300)")
        time.sleep(0.5)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
tile_list = driver.find_elements(By.XPATH, "//div[@class='GFY23']")
# for each tile, find necessary data and trim images set
for tile in tile_list:
    # gather img url, author, list of tags, trim url
    img_url = tile.find_element(By.XPATH, ".//img[@class='tB6UZ a5VGX']").get_attribute("srcset").split(" ")[-2]
    author_name = tile.find_element(By.XPATH, ".//a[@class='ZNlY9']").get_attribute("href").split("@")[-1]
    tags_div = tile.find_elements(By.XPATH, ".//div[@class='VZRk3']")
    tags_list_element = tile.find_elements(By.XPATH, ".//a[@class='IMl2x Ha8Q_']")
    tags = [tag.get_attribute("title") for tag in tags_list_element]
    # clean up tags list
    tags = [tag.split("image")[0].strip().casefold() for tag in tags]

    ## filter data
    if author_name in AUTHORS_TO_EXCLUDE:
        continue
    tags_set = set(tags)
    if len(TAGS_TO_EXCLUDE.intersection(tags_set)) > 0:
        continue

    ## image fits criteria, add to a data class and push to results
    result = ImageItem(img_url, author_name, tags)
    results.append(result)
# Write to CSV
with open('images.csv', 'w',) as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['url', 'author', 'tags'])
    for result in results:
        writer.writerow([result.image_url, result.author, result.tags])
driver.close()
