import hashlib
import sys
import threading

from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import desired_caps
from config import input_values
import constants
import re
import time
import os
import reporting
import glob
from multiprocessing import Process
from config import url
from comparison import comapare_data
import shutil

class DriverFactory() :

    visited_pages = []
    visited_page_source=[]
    visited_items = []
    blacklist = "Navigate Up"
    driver = None
    count=0


    def __init__(self, url, desired_caps):
        self.driver = self.create_driver(url, desired_caps)

    def create_driver(self, url, desired_caps):
        return(webdriver.Remote(url, desired_caps))

    def quit_driver(self):
        self.driver.quit()

    def crawl_app(self):
        start_activity = self.driver.current_activity
        print(self.driver.current_activity)
        start_page_source=self.driver.page_source
        if self.driver.page_source not in self.visited_page_source :
            self.visited_page_source.append(self.driver.page_source)
            print(str(self.driver.contexts))

            #WEBVIEW
            if bool(re.search("WEBVIEW_com.citrix.Receiver", str(self.driver.contexts), re.IGNORECASE)) :
                current_context="WEBVIEW_com.citrix.Receiver"
                self.driver.switch_to.context(current_context)
                try:
                    WebDriverWait(self.driver, constants.SMALL_TIMEOUT).until(EC.visibility_of("//a[@href]"))
                except:
                    pass
                list_of_links = self.driver.find_elements_by_xpath("//a[@href]")
                list_of_links = list_of_links + self.driver.find_elements_by_xpath("//button")
                list_of_inputs = self.driver.find_elements_by_xpath("//input")
                for item in list_of_inputs:
                    for text_to_enter in input_values.keys():
                        if bool(re.search(text_to_enter, str(item.get_attribute("name")) +
                                                         str(item.get_attribute("id")) +
                                                         str(item.text), re.IGNORECASE)):
                            item.send_keys(input_values[text_to_enter])
                for item in list_of_links:
                    print("++++++++++++++++++++++++++++++++++++++")
                    print(str(item.get_attribute("href")))
                    print("=======================================")
                    if (not bool(re.search(str(item.get_attribute("href")), self.blacklist, re.IGNORECASE))) \
                            and item.is_enabled() \
                            and item.is_displayed() \
                            and item.get_attribute("innerHTML") not in self.visited_items :
                        self.visited_items.append(item.get_attribute("innerHTML"))
                        activity_name = self.driver.current_activity
                        prev_page_source = self.driver.page_source
                        print("clicking item")
                        try:
                            item.click()
                        except:
                            try:
                                self.action_click(item)
                            except:
                                pass
                        print("clicked item")
                        # self.action_click(item)
                        try:
                            WebDriverWait(self.driver, constants.TIMEOUT).until(EC.invisibility_of_element(item))
                        except:
                            pass
                        result = hashlib.sha256(self.driver.page_source.encode())
                        self.take_screenshot(result.hexdigest())
                        if (prev_page_source != self.driver.page_source) :
                            self.crawl_app()
                self.driver.switch_to.context("NATIVE_APP")
            #NATIVE
            print(bool(re.search("NATIVE", str(self.driver.contexts), re.IGNORECASE)))
            if bool(re.search("NATIVE", str(self.driver.contexts), re.IGNORECASE)):
                try:
                    WebDriverWait(self.driver, constants.SMALL_TIMEOUT).until(EC.visibility_of("//*"))
                except:
                    pass
                list_of_elements = self.driver.find_elements_by_xpath("//*")
                item_dictionary = self.identify_element(list_of_elements)
                if "input" in item_dictionary :
                    for item in item_dictionary["input"] :
                        for text_to_enter in input_values.keys():
                            if bool(re.search(text_to_enter, str(item.get_attribute("text")) +
                                                        str(item.get_attribute("class")) +
                                                        str(item.get_attribute("resource-id")) +
                                                        str(item.get_attribute("content-desc"))) ):
                                item.send_keys(input_values[text_to_enter])
                if "button" in item_dictionary:
                    for item in item_dictionary["button"] :
                        print("++++++++++++++++++++++++++++++++++++++")
                        print(str(item.get_attribute("content-desc")))
                        print("=======================================")
                        if item.is_enabled() \
                                and (not bool(re.search(str(item.get_attribute("content-desc")), self.blacklist, re.IGNORECASE))) \
                                and item.get_attribute("innerHTML") not in self.visited_items:
                            self.visited_items.append(item.get_attribute("innerHTML"))
                            activity_name = self.driver.current_activity
                            prev_page_source = self.driver.page_source
                            try:
                                item.click()
                            except:
                                try:
                                    self.action_click(item)
                                except:
                                    pass
                            # item.click()
                            print("Clicking item")
                            try:
                                WebDriverWait(self.driver, constants.TIMEOUT).until(EC.invisibility_of_element(item))
                            except:
                                pass
                            EC.invisibility_of_element(item)
                            self.wait_for_load()
                            result = hashlib.sha256(self.driver.page_source.encode())
                            self.take_screenshot(result.hexdigest())
                            if (prev_page_source != self.driver.page_source):
                                self.crawl_app()
        #BACK BUTTON
        if start_page_source != self.driver.page_source :
            print("Backing")
            self.driver.back()

    def wait_for_load_buffer(self, prev_page_source):
        TIMEOUT = constants.LARGE_TIMEOUTS
        while (bool(re.search("loading", self.driver.page_source, re.IGNORECASE))
               or bool(re.search("spinner@", self.driver.page_source, re.IGNORECASE))
               or bool((not re.search("clickable=\"true\"", self.driver.page_source, re.IGNORECASE)))
               or bool(re.search("ProgressBar", self.driver.page_source, re.IGNORECASE))
               or prev_page_source == self.driver.page_source)  and TIMEOUT>0 :
            time.sleep(1)
            TIMEOUT = TIMEOUT-1

    def wait_for_load(self):
        TIMEOUT = constants.LARGE_TIMEOUTS
        time.sleep(1)
        while (bool(re.search("loading", self.driver.page_source, re.IGNORECASE))
               or bool(re.search("spinner@", self.driver.page_source, re.IGNORECASE))
               or bool((not re.search("clickable=\"true\"", self.driver.page_source, re.IGNORECASE)))
               or bool(re.search("ProgressBar", self.driver.page_source, re.IGNORECASE))) and TIMEOUT>0:
            time.sleep(1)
            TIMEOUT = TIMEOUT-1

    def identify_element(self, list_of_elements):
        item_dictionary = {}
        for item in list_of_elements:
            if bool(re.search("EditText", str(item.get_attribute("class")), re.IGNORECASE)):
                if "input" in item_dictionary.keys():
                    item_dictionary["input"] = item_dictionary["input"] + [item]
                else :
                    item_dictionary["input"] = [item]
            elif bool(re.search("button", str(item.get_attribute("class")), re.IGNORECASE)) \
                    and (str(item.get_attribute("text")) != ""
                         or str(item.get_attribute("text")) != ""):
                if "button" in item_dictionary.keys():
                    item_dictionary["button"] = item_dictionary["button"] + [item]
                else :
                    item_dictionary["button"] = [item]
            elif bool(re.search("TextView", str(item.get_attribute("class")), re.IGNORECASE)):
                if "text" in item_dictionary.keys():
                    item_dictionary["text"] = item_dictionary["text"] + [item]
                else :
                    item_dictionary["text"] = [item]
        return item_dictionary

    def action_click(self,element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.click()
        actions.perform()

    def take_screenshot(self, hashed_page):
        print("{:07d}".format(self.count))
        file_name = str("{:07d}".format(self.count)) + "__" + str(hashed_page) +'.png'
        filepath = os.path.join(constants.ROOT_DIR,"images", file_name)
        print(filepath)
        self.driver.save_screenshot(filepath)
        self.count= self.count +1


def run_crawler():
    runner = DriverFactory(url, desired_caps)
    while(1):
        try :
            runner.crawl_app()
        except Exception as e:
            try:
                print(e)
                runner.visited_pages.clear()
                runner.driver.back()
                runner.crawl_app()
            except Exception as e:
                print(e)

def report():
        print("REPORTING::")
        data = []
        files_list = glob.glob(os.path.join(constants.ROOT_DIR,"images",'') + "*")
        print("FILES:")
        print(files_list)
        for image in files_list :
            data.append({"name" : image , "description": "ID: "+ str(image.split("__")[1].split(".png")[0])})
        reporting.reporting(data, "TrueCrawler", "snapshots.html")

def crash_log_report():
    print("Starting crash log")
    os.system("adb logcat AndroidRuntime:E *:S > " + os.path.join(constants.ROOT_DIR,"CRASH_LOGS.txt"))


if __name__ == '__main__':

    if len(sys.argv)>1:
        constants.RUNNING_TIME = sys.argv[1]
        print("Running for Duration : "+ str(constants.RUNNING_TIME))

    print("___________________________________________________________")
    shutil.rmtree(os.path.join(constants.ROOT_DIR, "images", ''))
    try:
        os.mkdir(os.path.join(constants.ROOT_DIR, "images", ''))
    except OSError as error:
        print(error)
    
    print("___________________________________________________________")
    #ADB logs
    os.system(f"adb logcat -c")
    crashlog = Process(target=crash_log_report)
    crashlog.start()

    print("___________________________________________________________")
    #Crawler Run
    action_process = Process(target=run_crawler)
    action_process.start()
    action_process.join(timeout=constants.RUNNING_TIME)
    action_process.terminate()

    print("___________________________________________________________")
    #ADB log closure
    print("Logging Crash logs and Adb Logs")
    os.system("adb logcat -d > " + os.path.join(constants.ROOT_DIR,"ADB_LOGS.txt"))
    crashlog.terminate()

    print("___________________________________________________________")
    #Comparison
    comparison_process = Process(target=comapare_data)
    comparison_process.start()
    comparison_process.join()
    comparison_process.terminate()

    print("___________________________________________________________")
    #Reporting
    action_process2 = Process(target=report)
    action_process2.start()
    action_process2.join()
    action_process2.terminate()

