#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 23:38:57 2022

@author: moi
"""

#cves
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from assistant import parse_it, scroll_to_bottom
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from calendar import month_name
from pandas_gbq import to_gbq
import pandas as pd

def get_cves_details(driver, wait, today):
    
    #%% CVES
    #loop through the years + months & collect results
    
    cve_details_list = []
    
    years = list(range(2016,2023))
    month_numbers = list(range(1,13))
    
    for year in years:
        for month_number in month_numbers:
        
            cve_details_url = 'https://www.cvedetails.com/vulnerability-list/year-{}/month-{}/{}.html'.format(str(year), str(month_number), month_name[month_number])
            driver.get(cve_details_url)
    
            #move to the bottom to get all of the page links
            scroll_to_bottom(driver)
            page_section = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pagingb"]')))
            page_links = [i for i in page_section.find_elements(By.TAG_NAME,'a')]
            
            for l in range(0,len(page_links)):
                
                print(year, month_name[month_number], l)
                
                try:
                    #redeclare stale elements
                    scroll_to_bottom(driver)
                    page_section = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pagingb"]')))
                    link = [i for i in page_section.find_elements(By.TAG_NAME,'a')][l]
                    
                    link.click()
                    
                    soup = bs(driver.page_source, 'lxml') 
            
                    #find the page table
                    cve_table = soup.find('table', class_ = 'searchresults sortable')            
            
                    try:
                        this_cve_table = parse_it(cve_table)
                        #create dataframe from results
                        this_cve_table_df = pd.DataFrame(this_cve_table, columns = this_cve_table[0])
                        #drop out the first row
                        this_cve_table_df = this_cve_table_df.drop(this_cve_table_df.index[0])
                        cve_details_list.append(this_cve_table_df)
                      
                    except:
                         pass
                
                except TimeoutException:
                    pass
    
    cve_details_df = pd.concat(cve_details_list)
    
    #add the even indices under column '#' as descriptions to the prior row
    descriptions = cve_details_df['#'][1::2]
    descriptions_df = pd.DataFrame(descriptions)
    descriptions_df = descriptions_df.reset_index().drop('index', axis = 1).rename(columns = {'#':'description'})
    
    #drop out odd rows
    cve_details_to_keep = cve_details_df[::2]
    cve_details_to_keep = cve_details_to_keep.reset_index().drop('index', axis = 1)
    final_cve_details_df = cve_details_to_keep.merge(descriptions_df, left_index = True, right_index = True)
    final_cve_details_df = final_cve_details_df.drop_duplicates()
    
    #make columns lower case
    final_cve_details_df.columns = [x.lower() for x in final_cve_details_df.columns.values.tolist()]
    #insert underscores for spaces
    final_cve_details_df.columns = [x.replace(' ', '_') for x in final_cve_details_df.columns.values.tolist()]
    
    #store a local backup copy
    final_cve_details_df.to_csv('backup-data/cves-details-{}.csv'.format(today), index = False)
    
    #load to big query
    to_gbq(final_cve_details_df, 
           'cves.cves-table', 
           project_id = 'cyer-crime-360523', 
           if_exists = 'replace')
