#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 22:43:32 2022

@author: me
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 23:36:01 2022

@author: moi
"""

#google exploits
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        NoSuchElementException, 
                                        WebDriverException,
                                        TimeoutException)
from selenium.webdriver.support import expected_conditions as EC
from assistant import parse_it, scroll_to_bottom
from selenium.webdriver.common.by import By
from pandas_gbq import to_gbq, read_gbq
from bs4 import BeautifulSoup as bs
import pandas as pd
#initialize & launch driver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        NoSuchElementException, 
                                        WebDriverException,
                                        TimeoutException)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import datetime
from time import time, sleep

#start the timer
start_time = time()

#set today's date
today = datetime.today().strftime('%d-%m-%Y')

#initialize Google Big Query Project ID
project_id = 'cyber-crime-360523'

#initialize automation
ignored_exceptions = (ElementClickInterceptedException,
                      StaleElementReferenceException,
                      NoSuchElementException, 
                      WebDriverException,
                      TimeoutException)

chrome_options = Options()
#chrome_options.add_argument("--headless")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) 
wait = WebDriverWait(driver, 6, poll_frequency=6, ignored_exceptions=ignored_exceptions)


def google_processing_check(wait):
    #Checks for the 'Processing' modal
    try:
        wait.until(EC.visibility_of_element_located((By.ID, 'exploits-table_processing')))
    except ignored_exceptions:
        pass

def scroll_up(driver):
    driver.execute_script("scrollBy(0,250);")

google_exploit_db = 'https://www.exploit-db.com/' 
driver.get(google_exploit_db)

google_processing_check(wait)

#change show dropdown to 120
show_xpath = '/html/body/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div[1]/div/label/select'
wait.until(EC.element_to_be_clickable((By.XPATH, show_xpath))).click()

show120_xpath = '/html/body/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/div[1]/div/label/select/option[4]'
wait.until(EC.element_to_be_clickable((By.XPATH, show120_xpath))).click()

scroll_to_bottom(driver)

#get the total number of exploit records
total_exploits_str = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'dataTables_info')))
total_exploits = total_exploits_str.text[20:26] 
total_exploits = total_exploits.replace(',','')
total_exploits = int(total_exploits)
print('Total exploits: ', total_exploits)

total_pages = 376
    
google_exploit_list = []

for i in range(1, total_pages + 1): 
    
    google_processing_check(wait)
    
    print('google exploits - ', i)

    soup = bs(driver.page_source, 'lxml') 

    #find all the page tables
    google_table = soup.find('table', class_ = 'table table-striped table-bordered display dataTable no-footer dtr-inline')            

    this_google_table = parse_it(google_table)
    
    #convert to dataframe and drop the first row
    this_google_table_df = pd.DataFrame(this_google_table, columns = this_google_table[0])
    this_google_table_df = this_google_table_df.drop(this_google_table_df.index[0])
    
    #append the results
    google_exploit_list.append(this_google_table_df)

    #check for processing modal                    
    google_processing_check(wait)
    
    #scroll to bottom
    scroll_to_bottom(driver)
    
    try:
        next_css = '#exploits-table_next'
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_css))).click()
    
    except ignored_exceptions:
        
        try:
            #check for processing modal
            google_processing_check(wait)
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'paginate_button page-item next'))).click() # id="exploits-table_next"><a href="#" aria-controls="exploits-table" data-dt-idx="9" tabindex="0" class="page-link">Next</a></li>       
        except:
            break
    
    scroll_up(driver)
    
    sleep(1)

#concatenate the list of dataframes
google_exploits_df = pd.concat(google_exploit_list)   

#convert the date column into a timestamp
google_exploits_df['Date'] = pd.to_datetime(google_exploits_df['Date'])

#remove any duplicates (if exists)
google_exploits_df = google_exploits_df.drop_duplicates()

#remove periods
google_exploits_df.columns = [x.replace('.', '') for x in google_exploits_df.columns.values.tolist()]

#remove parentheses
google_exploits_df.columns = [x.replace('(', '').replace(')','') for x in google_exploits_df.columns.values.tolist()]

#change out "# of" for "no_of_"
google_exploits_df.columns = [x.replace('#', 'no') for x in google_exploits_df.columns.values.tolist()]
  
#make columns lower case
google_exploits_df.columns = [x.lower() for x in google_exploits_df.columns.values.tolist()]

#insert underscores for spaces
google_exploits_df.columns = [x.replace(' ', '_') for x in google_exploits_df.columns.values.tolist()]

#make a local backup copy
google_exploits_df.to_csv('backup-data/google-exploits-{}.csv'.format(today), index = False)

#%% Google Big Query

#load to big query
to_gbq(google_exploits_df, 
       'google_exploits.google-exploits-table', 
       project_id = project_id, 
       if_exists = 'replace')

#Check loaded table size
table_size_sql = """ select count(*) from `google_exploits.google-exploits-table` """
table_size = read_gbq(table_size_sql, project_id = project_id)
table_size = table_size.iloc[0,0]

print('Google Exploits table size: ', table_size)

#Compare this to the total exploits value (collected earlier on)

if total_exploits == table_size:
    print('Google Exploits - Big Query Records Count - Successful')

else:
    print('ERROR! Google Exploits Record Count != Big Query Table Count')

