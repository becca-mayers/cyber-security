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
#from iana_ports import  get_iana_ports
from ic3_reports import get_ic3
from datetime import datetime
from time import time


start_time = time()

today = datetime.today().strftime('%d-%m-%Y')

driver, wait = launch_driver()

get_cves_details(driver, wait, today)
get_google_exploits(driver, wait, today)
#get_iana_ports(driver, wait)
get_ic3(driver, wait, today)

driver.close()

end_time = time()

total_time = (end_time - start_time)/60

print('total runtime: ', total_time)
