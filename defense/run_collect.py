import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException as wde
import subprocess
import sys
import random
from tbselenium.tbdriver import TorBrowserDriver
from multiprocessing import Process


def run_browser(type, address, timeout):
    print("!!!!!!")
    if type == 'chrome':
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver', options=chrome_options)

        driver.get(address)
        time.sleep(timeout)
        driver.quit()


def detection_attack(type, idx, address_lists, sen_lists):
    for i, row in address_lists.iterrows():
        name = row['0']
        address = row['1']
        # state = random.randint(1,10)
        # if state < 6:
        #     print("obf!!!")
        print(name)
        if type == 'chrome':
            url = "file:///home/erc/PycharmProjects/cache_attack/detection/attack_chrome_b.html"
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            # driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver', chrome_options=chrome_options)
            try:
                driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver',
                                          options=chrome_options)
            except wde as e:
                print("\nChrome crashed on launch:")
                print(e)
                print("Trying again in 10 seconds..")
                time.sleep(10)
                driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver',
                                          options=chrome_options)
                print("Success!\n")
            except Exception as e:
                raise Exception(e)
            subprocess.Popen(["./detection"])

            p = Process(target=run_browser, args=(type, sen_lists.iloc[i, 1], 30))
            p.start()

            driver.get(url)
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "clickMe")))
            input_box = driver.find_element_by_id('address')
            input_box.send_keys(address)
            button.click()

            # time.sleep(30)
            # data = driver.find_element_by_tag_name("body").text
            # line = list(data.split(','))
            # df = pd.DataFrame(line)
            # df.to_csv('/home/erc/PycharmProjects/cache_attack/data/obf_chrome_' + name + '_' + str(idx) + '.csv')
            driver.quit()


def site_connection_check(type, address_lists):
    reachable_list = []
    reachable = -1
    for i, row in address_lists.iterrows():
        name = row['0']
        address = row['1']
        if type == 'chrome':
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            # driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver', chrome_options=chrome_options)
            try:
                driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver',
                                          options=chrome_options)  # Optional argument, if not specified will search path.
            except wde as e:
                print("\nChrome crashed on launch:")
                print(e)
                print("Trying again in 10 seconds..")
                time.sleep(10)
                driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver',
                                          options=chrome_options)
                print("Success!\n")
            except Exception as e:
                raise Exception(e)
            driver.get(address)
            time.sleep(5)
            data = driver.find_element_by_tag_name("body").text
            reachable = data.find('This site can’t be reached')
            if reachable == -1:
                reachable_list.append([name,0])
            else:
                reachable_list.append([name,1])
            time.sleep(1)
            driver.quit()

        if type == 'tor':
            with TorBrowserDriver("/home/erc/Downloads/tor-browser_en-US/") as driver:

                # driver.execute_script("window.open('" + address + "');")
                try:
                    driver.get(address)
                    data = driver.find_element_by_tag_name("body").text
                    # reachable = data.find('can’t be reached')
                    # if reachable == -1:
                    reachable_list.append([name, 1])
                    # else:
                    #     reachable_list.append([name, 0])
                except:
                    time.sleep(1)
                    reachable_list.append([name,0])
                    pass

                driver.quit()

        print(name + '_'  + str(reachable))
    return reachable_list

def attack(type, idx, address_lists):
    for i, row in address_lists.iterrows():
        name = row['0']
        address = row['1']
        # state = random.randint(1,10)
        # if state < 6:
        #     print("obf!!!")
        # subprocess.Popen(["./def_mp"])
        if type == 'chrome':
            url = "file:///home/erc/PycharmProjects/cache_attack/auto_cache_attack/attack_chrome.html"
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            # driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver', chrome_options=chrome_options)
            try:
                driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver',
                                          options=chrome_options)  # Optional argument, if not specified will search path.
            except wde as e:
                print("\nChrome crashed on launch:")
                print(e)
                print("Trying again in 10 seconds..")
                time.sleep(10)
                driver = webdriver.Chrome('/home/erc/PycharmProjects/cache_attack/driver/chromedriver',
                                          options=chrome_options)
                print("Success!\n")
            except Exception as e:
                raise Exception(e)
            subprocess.Popen(["./def_mp"])
            driver.get(url)
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "clickMe")))
            input_box = driver.find_element_by_id('address')
            input_box.send_keys(address)
            button.click()
            # subprocess.Popen("python3 open_pages.py",shell=True)
            # run_browser(type, "https://www.youtube.com/", timeout)
            data = driver.find_element_by_tag_name("body").text
            line = list(data.split(','))
            df = pd.DataFrame(line)
            df.to_csv(
                '/home/erc/PycharmProjects/cache_attack/data/obf_linux_chrome/random_obf_linux_chrome_' + name + '_' + str(
                    idx) + '.csv')
            time.sleep(1)
            driver.quit()

        if type == 'firefox':
            url = "file:///home/erc/PycharmProjects/cache_attack/auto_cache_attack/attack_firefox.html"
            try:
                driver = webdriver.Firefox()
            except wde as e:
                print("\nChrome crashed on launch:")
                print(e)
                print("Trying again in 10 seconds..")
                time.sleep(10)
                driver = webdriver.Firefox()
                print("Success!\n")
            except Exception as e:
                raise Exception(e)
            subprocess.Popen(["./def_mp"])
            try:
                driver.execute_script("window.open('" + address + "');")
                driver.get(url)
            except:
                print("fail openning..")
                time.sleep(5)
                driver.execute_script("window.open('" + address + "');")
                driver.get(url)
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "clickMe")))
            # time.sleep(5)
            button.click()
            try:
                data = driver.find_element_by_tag_name("body").text
            except:
                time.sleep(30)
                pass
            data = driver.find_element_by_tag_name("body").text
            line = list(data.split(','))
            df = pd.DataFrame(line)
            df.to_csv('/home/erc/PycharmProjects/cache_attack/data/obf_linux_ff/obf_linux_ff_' + name + '_' + str(
                idx) + '.csv')
            driver.quit()
            time.sleep(1)

        if type == 'tor':
            url = "file:///home/erc/PycharmProjects/cache_attack/auto_cache_attack/attack_tor.html"
            with TorBrowserDriver("/home/erc/Downloads/tor-browser_en-US/") as driver:

                driver.execute_script("window.open('" + address + "');")
                driver.get(url)
                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "clickMe")))
                button.click()
                time.sleep(1)
                try:
                    data = driver.find_element_by_tag_name("body").text
                except:
                    time.sleep(50)
                    pass
                line = list(data.split(','))
                df = pd.DataFrame(line)
                df.to_csv('/home/erc/PycharmProjects/cache_attack/data/obf_linux_tor/ow_obf_linux_tor_' + name + '_' + str(
                    idx) + '.csv')
                driver.quit()

        print(name + '_' + str(idx) + " finished!")
        # time.sleep(1)


if __name__ == '__main__':
    # browser = 'firefox'
    # browser = 'chrome'
    browser = 'tor'

    address_lists = pd.read_csv('/home/erc/PycharmProjects/cache_attack/address_list.csv')
    # address_lists = pd.read_csv('/home/erc/PycharmProjects/cache_attack/open_world_list.csv')
    # address_list = address_lists.iloc[:500, :]

    # sen_list = address_lists.iloc[1000:1500, :]
    # for i in range(25):
    #     b_attack(browser, i, address_lists)
    # subprocess.Popen(["./def_mp"])
    # for i in range(50, 100):
    #     attack(browser, i, address_lists)
    reachable_list = site_connection_check(browser,address_lists)
    df = pd.DataFrame(reachable_list)
    df.to_csv("reachable_list.csv")
    # attack(browser, 0, address_lists)
    # detection_attack(browser, 0, address_list, sen_list)
