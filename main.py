from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import re
from tkinter import *
import subprocess
import sys
import sqlite3
import datetime

# change dir to a custom path to work from
os.chdir(r'C:\Users\scorb\OneDrive\Documents\GitHub\Practice\selenium course\usage_app')

chrome_options = Options()
# add headless argument to enable running in the background
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")  # Set log level to "warning" or "fatal"
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Exclude logging
os.environ['WDM_LOG_LEVEL'] = '0'  # Disable logging for WebDriverManager (if used)

# redirection of the log and error messages to an external files
sys.stdout = open(r'output.log', 'w')
sys.stderr = open(r'error.log', 'a')

# add the webdriver manager of chrome to PATH
os.environ['PATH'] += r'C:\Users\scorb\OneDrive\Documents\GitHub\Practice\selenium course\drivers'

# open the file of login info
handle = open(r'd:\Work\code\files\python\info_of_usage_app.txt','r')
storage = handle.readline()

# get the login info from file
user_name = re.search(r'.+\-' , storage).group()[:-1]
password = re.search(r'\-.+' , storage).group()[1:]


def close_all():
    # function to close all instances
    global driver
    driver.close()
    handle.close()
    root.quit()
    
def open_fun():
    # the main function of the app
    try:
        # the connection to the database
        db = sqlite3.connect(r'data.db')
        cursor = db.cursor()
        cursor.execute('create table if not exists data (day text , time text , usage text, state text)')
        
        # initial values to the window labels
        usage_label.config(text='# Usage')
        remaining_label.config(text='# Remaining')
        current_state.config(text='# State')
        # intiation of the webdriver
        global driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(15)
        # the website to scrap
        driver.get(r'https://my.te.eg/user/login')

        # insertion of the user_name
        user = driver.find_element(by='id', value='login-service-number-et')
        user.send_keys(user_name)
        
        # insertion of the password
        pass_word = driver.find_element(by=By.ID, value='login-password-et')
        pass_word.send_keys(password)

        # selection of an item of the list
        list_options = driver.find_element(by=By.NAME, value='numberType')
        list_options.click()
        
        internet = driver.find_element(by=By.CSS_SELECTOR, value='[aria-label="Internet"]')
        internet.click()

        # login click
        login = driver.find_element(by=By.ID,value='login-login-btn')
        login.click()

        # select and get the quota 
        usage_return = driver.find_element(by=By.CSS_SELECTOR, value='[class="remaining-details ng-star-inserted"]') # usage
        usage_text = re.search(r'[0-9]+\.[0-9]+',usage_return.text)
        usage = usage_text.group()

        text_click = driver.find_element(by=By.CSS_SELECTOR, value='[class="text-black underline"]')
        text_click.click()

        # select and get of the remaining days
        remaining_days_return = driver.find_element(by=By.CSS_SELECTOR, value='[class="mr-auto"]') # remaining_days
        remaining_days_return_text = re.search(r' [0-9] ', remaining_days_return.text).group()
        remaining_days = remaining_days_return_text #.group()

        # calculation of the quota state
        state = float(usage) - (140/30)*int(remaining_days)
        
        # selection of labels colors depends on the state 
        if state > 0:
            detector_usage = '#89f599'
        else:
            detector_usage = '#f59089'
            
            
        if int(remaining_days) > 2:
            detector_days = '#89f599'
        else:
            detector_days = '#f59089'

        # setting the labels to the retrieved values
        usage_label.config(text='Usage is: '+usage)

        remaining_label.config(text='Remaining days are: '+str(remaining_days),background=detector_days)

        current_state.config(text='State is: '+str(state)[0:5],background=detector_usage)
    except:
        # error handling by recalling the main function
        print('error occured\n')
        open_fun()
        
    finally:
        # insertion of the process date, time and values into the database
        cursor.execute(f'''insert into data values (
                       "{datetime.datetime.now().date()}" ,
                       "{datetime.datetime.now().time()}",
                       "{usage}",
                       "{str(state)[0:5]}")'''
                       )
        db.commit()
        db.close()

# the window intiation and customization
root = Tk()
root.title('Usage')
root.iconbitmap(r'download.ico')
root.minsize(326,226)

# open button with function open_fun
open_btn = Button(root,text='Open',command=open_fun, font=('arial',20),activebackground='#dbedff')
open_btn.grid(row=0,column=0,sticky=W+E)

# close all button with function close_all
close_all = Button(root, text='Close All',command=close_all, font=('arial',20),activebackground='#dbedff')
close_all.grid(row=5,column=0,sticky=W+E)

# label to display quota usage
usage_label = Label(root,text='# Usage',width=20, font=('arial',20),background='#f5e6b0')
usage_label.grid(row=1,column=0,sticky=W+E)

# label to display remaining days of qouta
remaining_label = Label(root,text='# Remaining', font=('arial',20))
remaining_label.grid(row=2,column=0,sticky=W+E)

# label to display the qouta state
current_state = Label(root,text='# State', font=('arial',20))
current_state.grid(row=3,column=0,sticky=W+E)


root.mainloop()