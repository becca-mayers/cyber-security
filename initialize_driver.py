#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 23:31:24 2022

@author: moi
"""


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



def launch_driver():
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

    return driver, wait