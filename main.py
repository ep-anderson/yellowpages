from selenium import webdriver
import time
import re
import pandas as pd
import csv
from bs4 import BeautifulSoup


def tsv_to_list(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter="\t")
        data = list(reader)
        return data


def find_and_add_div(div, indicator, type):
    
    #extracting result from html
    if type == 'class':
        result = div.find("div", {"class" : "{}".format(indicator)})
        
    if type == 'recompile':
        result = div.find(re.compile('^h[2]$'))
    
    #adding n/a for none values
    if result:
        return result.text
    else:
        return 'N/A'

### INPUT DATA ###
businesses = tsv_to_list('businesses.tsv')

#cities must be in "city, STATE" format for accurate search
cities = tsv_to_list('cities.tsv')


### WEBDRIVER CREATION ###
#setting options for browser
options = webdriver.FirefoxOptions()

#creates browser
driver = webdriver.Firefox(executable_path="FILEPATH\\geckodriver.exe", options=options)


### ITERATING OVER INPUT DATA ###

#final list of lists used to convert to df
yellowpage_data = []

#iterates through each business
for business in businesses:

    #iterates through each city listed
    for city in cities:
        
        #iterates through each page, range number can be altered if you like to only have a certain amount of pages per businesscity
        for page_number in range(99):
            
            #variable that counts how many times a new card is added to yellowpage_data. If 0 at the end of the loop, breaks for loop
            count = 0
        
            #creates and calls url based on location and business type
            url = f'https://www.yellowpages.com/search?search_terms={business}&geo_location_terms={city}&s=average_rating&page={page_number}'
            driver.get(url)

            content = driver.page_source
            

            soup = BeautifulSoup(content, 'html.parser')


            ###Locating elements###
            
            #finds all cards from site
            divs = soup.find_all("div", {'class':'info'})
            
            #iterates through each card
            for div in divs:
                
                #scrapes name, phone, address and state
                phone = find_and_add_div(div, "phones phone primary", 'class')
                address = find_and_add_div(div, "street-address", 'class')
                state = find_and_add_div(div, "locality", 'class')
                name = find_and_add_div(div, None, 'recompile')[3:].strip()
                info_list = [name, phone, address, state]
                
                #filters out ad cards and adds to main list
                if phone != 'N/A':
                    count += 1
                    yellowpage_data.append(info_list)
                    
            if count == 0:
                break
            
            time.sleep(3)
                
             
df = pd.DataFrame(yellowpage_data, columns=['Company Name', 'Phone Number', 'Address', 'City/State/Zip'])

df.to_csv('yellowpagesdata.csv',index=False)
         













