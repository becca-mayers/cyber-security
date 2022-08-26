#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 23:30:30 2022

@author: me
"""

#assistant


#%% Helper functions
def parse_it(table):       
    rows = []
    trs = table.find_all('tr')
    header_row = [td.get_text(strip=True) for td in trs[0].find_all('th')] # header row
    if header_row: # if there is a header row include first
        rows.append(header_row)
        trs = trs[1:]
    for tr in trs: # for every table row
        rows.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
    return rows

def scroll_to_bottom(driver):
    return driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def scroll_200(driver):
    return driver.execute_script("window.scrollTo(0, window.scrollY + 200)")