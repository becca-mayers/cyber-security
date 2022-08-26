#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 21:33:11 2022

@author: moi
"""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from assistant import parse_it, scroll_200
from bs4 import BeautifulSoup as bs
from random import randint
from time import sleep
import pandas as pd

def get_insecure_ports(driver, wait):


    url = 'https://www.speedguide.net/ports.php?filter=risk&p=3'
    next_selector = '#content > table:nth-child(6) > tbody > tr > td:nth-child(2) > div > a:nth-child(3)'
    next_xpath = '/html/body/table/tbody/tr/td[2]/table[2]/tbody/tr/td[2]/div/a[2]'
    
    driver.get(url)
    
    #randomizing length of sleep because this site refuses to connect otherwise
    sleep(randint(0,5))
    
    #get all div_class = "ports" find 'a' collect hrefs
    first_port = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'ports')))[0]
    
    #find tag 'a' class = button for the next button
    first_port.find_element(By.TAG_NAME, 'a').click() 
    
    sleep(randint(0,5))
    
    port_table_list = []
    
    for i in range(0, 3392):
        
        print(i, 'of 3392')
        
        #switch to soup
        soup = bs(driver.page_source, 'lxml') 
        
        #find all the page tables
        table = soup.find('table', class_ = 'port')
        this_table = parse_it(table)
        port_table_list.append(this_table)
    
        sleep(randint(0,5))
        
        try:
            #click next button using its selector
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_selector))).click()   
        except: 
            
            scroll_200(driver)
            #click next button using its full xpath
            wait.until(EC.element_to_be_clickable((By.XPATH, next_xpath))).click()
            
        sleep(randint(0,5))
    
    port_dfs = []
    for i in port_table_list:
        this_df = pd.DataFrame(i)
        this_df.columns = this_df.iloc[0,:]
        this_df = this_df.drop([0], axis = 0)
        port_dfs.append(this_df)
    
    ports = pd.concat(port_dfs)
    ports.to_csv('data/insecure-ports.csv', index = False)
