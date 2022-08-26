#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 13:20:35 2022

@author: moi
"""

#iana ports
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from assistant import parse_it
from pandas_gbq import to_gbq
from datetime import datetime
from random import randint
from time import sleep
import pandas as pd

def get_iana_ports(driver, wait):
    
    #iana port table
    iana_ports_url = 'https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml'
    
    driver.get(iana_ports_url)
    
    iana_list = []
    
    for i in range(144):
        
        #switch to soup
        soup = bs(driver.page_source, 'lxml') 
        
        #find all the page tables
        table = soup.find('table')
        iana_table = parse_it(table)
        iana_df = pd.DataFrame(iana_table)
        iana_df.columns = iana_df.iloc[0,:]
        iana_df = iana_df.drop([0], axis = 0)
        iana_list.append(iana_df)
        
        #get next page
        next_css = 'div.pagination:nth-child(6) > a:nth-child(1)'
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_css))).click()
        
        sleep(randint(0,5))
    
    #form dataframe from the collected list
    final_iana = pd.concat(iana_list)
    
    #store a local backup copy 
    today = datetime.today().strftime('%d-%m-%Y')
    final_iana.to_csv('backup-data/iana_ports-{}.csv'.format(today), index = False)
    
    #load to big query
    to_gbq(final_iana, 
           'iana.iana', 
           project_id = 'sunlit-center-360304', 
           if_exists = 'replace')
    
    return final_iana

def get_rfc_editor(driver, wait, final_iana):
    
    #%% RFC Editor
    
    final_iana['Reference'] = final_iana['Reference'].str.replace('[','').str.replace(']','')
    references = final_iana['Reference'].drop_duplicates().tolist()[1:]
    
    reference_list = []
    for reference in references:
        
        ref_dict = {}
        
        base_url = 'https://www.rfc-editor.org/rfc/{}.html'.format(str(reference)).lower()
        
        driver.get(base_url)
        
        sleep(randint(0,5))  
        
        #switch to soup
        soup = bs(driver.page_source, 'lxml') 
        
        #find all the page tables
        pre_text = soup.find('body').get_text()
        
        ref_dict['reference'] = reference
        ref_dict['text'] = pre_text
        
        ref_temp_df = pd.DataFrame.from_dict([ref_dict])
        
        reference_list.append(ref_temp_df)
    
    reference_df = pd.concat(reference_list)
    reference_df.to_csv('backup-data/rfc_editor.csv', index = False)
    
    #store a local backup copy 
    today = datetime.today().strftime('%d-%m-%Y')
    reference_df.to_csv('backup-data/rfc_editor-{}.csv'.format(today), index = False)
    
    #load to big query
    to_gbq(reference_df, 
           'rfc_editor.rfc_editor', 
           project_id = 'sunlit-center-360304', 
           if_exists = 'replace')


