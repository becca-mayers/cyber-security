#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 16:05:16 2022

@author: rebecca
"""

#ic3
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from assistant import parse_it
from pandas_gbq import to_gbq
from time import sleep
import pandas as pd

def get_ic3(driver, wait, today):

    ic3_years = list(range(2016,2022))

    ic3_list = []

    for ic3_year in ic3_years:
        
        ic3_url = 'https://www.ic3.gov/Media/PDF/AnnualReport/{}State/StateReport.aspx'.format(str(ic3_year))
        
        driver.get(ic3_url)
        
        for i in range(2,59):  
        
            #get selected state from site title
            state_dropdown_xpath = '/html/body/div/form/header/div[2]/h1'
            selected_state = wait.until(EC.element_to_be_clickable((By.XPATH, state_dropdown_xpath))).text
            
            print(ic3_year, selected_state)
        
            #switch to soup
            soup = bs(driver.page_source, 'lxml') 
        
            #find all the page tables
            ic3_tables = soup.find_all('table', class_ = 'crimetype')

            ic3_table_list = []
            
            for ic3_table in ic3_tables:

                #parse table
                this_ic3_table = parse_it(ic3_table)
                
                #convert to dataframe, set headers
                this_ic3_table_df = pd.DataFrame(this_ic3_table, columns = this_ic3_table[0])
                
                #drop the first row
                this_ic3_table_df = this_ic3_table_df.drop(this_ic3_table_df.index[0])
                
                #handle the column's layout
                first_ic3_subset_df = this_ic3_table_df.iloc[:,0:2]
                second_ic3_subset_df = this_ic3_table_df.iloc[:,2:4]
                ic3_df = pd.concat([first_ic3_subset_df, second_ic3_subset_df])
                
                #insert state and source
                ic3_df['state'] = selected_state
                ic3_df['year'] = ic3_year
                ic3_df['url'] = ic3_url
                
                ic3_table_list.append(ic3_df)

            #bring it all together
            ic3_dff = ic3_table_list[1].merge(ic3_table_list[0],
                                              on = ['Crime Type', 'state', 'year']).merge(ic3_table_list[2], 
                                                                                          on = ['Crime Type', 'state', 'year'])
            #drop duplicates (if exists)
            ic3_dff = ic3_dff.drop_duplicates()

            #reorder
            ic3_dfff = ic3_dff[['Crime Type', 'state', 'year', 'Subject Count', 'Victim Count', 'Loss Amount']]

            #make columns lower case
            ic3_dfff.columns = [x.lower() for x in ic3_dfff.columns.values.tolist()]

            #replace column spaces with underscores
            ic3_dfff.columns = [x.replace(' ','_') for x in ic3_dfff.columns.values.tolist()]
            
            #add to the list
            ic3_list.append(ic3_dfff)
            
            #update the url
            updated_url = ic3_url + '#?s={}'.format(str(i))
            
            #get the updated url
            driver.get(updated_url)
            
            sleep(3)        

    #put it all together
    final_ic3_dff = pd.concat(ic3_list)

    #remove duplicates and null records (if exist)
    final_ic3_dff = final_ic3_dff.drop_duplicates()
    final_ic3_dff = final_ic3_dff.dropna(subset = ['subject_count', 'loss_amount', 'victim_count'])

    #clean up the $ & , formatting
    final_ic3_dff['loss_amount'] = final_ic3_dff['loss_amount'].str.replace('$','', regex = False).str.replace(',','', regex = False)
    final_ic3_dff['subject_count'] = final_ic3_dff['subject_count'].str.replace(',','', regex = False)
    final_ic3_dff['victim_count'] = final_ic3_dff['victim_count'].str.replace(',','', regex = False)
    final_ic3_dff = final_ic3_dff.reset_index().drop('index', axis = 1)
    
    #convert the non-null counts/amounts into integer type
    for i in range(0, len(final_ic3_dff.index)):
        loss_amount = final_ic3_dff.loc[i, 'loss_amount']
        if loss_amount is not None:
            loss_amount = int(loss_amount)
            final_ic3_dff.loc[i,'loss_amount'] = loss_amount
        
        subject_count = final_ic3_dff.loc[i, 'subject_count']
        if subject_count is not None:
            subject_count = int(subject_count)
            final_ic3_dff.loc[i,'subject_count'] = subject_count
        
        victim_count = final_ic3_dff.loc[i, 'victim_count']
        if victim_count is not None:
            victim_count = int(victim_count)
            final_ic3_dff.loc[i,'victim_count'] = victim_count

    #save copy locally
    final_ic3_dff.to_csv('backup-data/ic3_data-{}.csv'.format(today), index = False)

    #load to big query
    to_gbq(final_ic3_dff, 
           'ic3.ic3-table', 
           project_id = 'cyber-crime-360523', 
           if_exists = 'replace')
    