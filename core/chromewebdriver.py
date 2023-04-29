import sys
import pandas as pd
import numpy as np
import atexit
from selenium import webdriver

def download_headless_chrome(driver: webdriver, download_dir: str):
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {
            'cmd': 'Page.setDownloadBehavior',
            'params': {
                'behavior': 'allow',
                'downloadPath': download_dir
            }
        }
        driver.execute("send_command", params)


def close_chrome(chrome: webdriver):
    def close():
        chrome.close()
    return close


def generate_chrome(
    driver_path: str,
    download_path: str,
    headless: bool=False #크롬 창 숨기기(False: 안숨기기 / True:숨기기)
    ) -> webdriver:

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if headless:
        options.add_argument('headless')
        options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs', {
        'download.default_directory': download_path,
        'download.prompt_for_download': False,
    })
    
    browser = webdriver.Chrome(executable_path=driver_path, options=options)

    if headless:
        download_headless_chrome(browser, download_path)

    atexit.register(close_chrome(browser))

    return browser