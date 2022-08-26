#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 23:36:46 2022

@author: moi
"""

#main
from google_exploits import get_google_exploits
from initialize_driver import launch_driver
from cves_details import get_cves_details
from ic3_reports import get_ic3
from datetime import datetime
from time import time

#start the timer
start_time = time()

#set today's date
today = datetime.today().strftime('%d-%m-%Y')

#initialize Google Big Query Project ID
project_id = 'cyber-crime-360523'

#launch the driver
driver, wait = launch_driver()

#get cves
get_cves_details(driver, wait, today, project_id)

#get google exploits
get_google_exploits(driver, wait, today, project_id)

#get ic3
get_ic3(driver, wait, today, project_id)

#close out the driver
driver.close()

#end the timer
end_time = time()

total_time = (end_time - start_time)/60
print('total runtime: ', total_time)
