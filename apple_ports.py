#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 13:20:19 2022

@author: moi
"""

from bs4 import BeautifulSoup as bs
from assistant import parse_it
import pandas as pd


def get_apple_ports(driver):
    
    #ports used by Apple products
    apple_ports_url = 'https://support.apple.com/en-us/HT202944'
    
    driver.get(apple_ports_url)
    
    #switch to soup
    soup = bs(driver.page_source, 'lxml') 
    
    #find all the page tables
    table = soup.find('table')
    apple_table = parse_it(table)
    apple_df = pd.DataFrame(apple_table)
    apple_df.columns = apple_df.iloc[0,:]
    apple_df = apple_df.drop([0], axis = 0)
    apple_df.to_csv('data/apple_ports.csv', index = False)
