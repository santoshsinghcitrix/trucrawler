from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import desired_caps
from config import input_values
import constants
import re
import time
import os


class DriverFactory() :

    visited_pages = []
    blacklist = "Navigate Up"
    driver = None

    def __init__(self, url, desired_caps):
        self.driver = self.create_driver(url, desired_caps)

    def create_driver(self, url, desired_caps):
        return(webdriver.Remote(url, desired_caps))

    def quit_driver(self):
        self.driver.quit()

    def crawl_app(self):
        print(self.driver.current_activity)
        self.wait_for_load()
        start_activity = self.driver.current_activity

        if self.driver.current_activity not in self.visited_pages :
            self.visited_pages.append(self.driver.current_activity)
            list_of_elements = self.driver.find_elements_by_xpath("//*")
            item_dictionary = self.identify_element(list_of_elements)
            if "input" in item_dictionary :
                for item in item_dictionary["input"] :
                    for text_to_enter in input_values.keys():
                        if re.search(text_to_enter, str(item.get_attribute("text")) +
                                                    str(item.get_attribute("class")) +
                                                    str(item.get_attribute("resource-id")) +
                                                    str(item.get_attribute("content-desc"))) :
                            item.send_keys(input_values[text_to_enter])
            if "button" in item_dictionary:
                for item in item_dictionary["button"] :
                    if re.search("button", str(item.get_attribute("class")), re.IGNORECASE) \
                            and EC.element_to_be_clickable(item) \
                            and not re.search(str(item.get_attribute("content-desc")), self.blacklist, re.IGNORECASE):
                        print(item.get_attribute("class"))
                        activity_name = self.driver.current_activity
                        prev_page_source = self.driver.page_source
                        item.click()
                        try:
                            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(item))
                        except:
                            pass
                        EC.invisibility_of_element(item)
                        self.wait_for_load_buffer(prev_page_source)
                        print(self.driver.page_source)
                        self.crawl_app()

        self.driver.back()

    def wait_for_load_buffer(self, prev_page_source):
        while (re.search("load", self.driver.page_source, re.IGNORECASE)
               or re.search("spinner", self.driver.page_source, re.IGNORECASE)
               or (not re.search("clickable=\"true\"", self.driver.page_source, re.IGNORECASE))
               or re.search("ProgressBar", self.driver.page_source, re.IGNORECASE)
               or prev_page_source == self.driver.page_source):
            time.sleep(1)

    def wait_for_load(self):
        while ("load" in self.driver.page_source
               or "spinner" in self.driver.page_source
               or (not ("clickable=\"true\"" in self.driver.page_source))
               or "ProgressBar" in self.driver.page_source):
            time.sleep(1)

    def identify_element(self, list_of_elements):
        # list_of_elements = self.driver.find_elements_by_xpath("//*")
        item_dictionary = {}
        for item in list_of_elements:
            if re.search("EditText", str(item.get_attribute("class")), re.IGNORECASE):
                if "input" in item_dictionary.keys():
                    item_dictionary["input"] = item_dictionary["input"] + [item]
                else :
                    item_dictionary["input"] = [item]
            elif re.search("button", str(item.get_attribute("class")), re.IGNORECASE) or EC.element_to_be_clickable(item):
                if "button" in item_dictionary.keys():
                    item_dictionary["button"] = item_dictionary["button"] + [item]
                else :
                    item_dictionary["button"] = [item]
            elif re.search("TextView", str(item.get_attribute("class")), re.IGNORECASE):
                if "text" in item_dictionary.keys():
                    item_dictionary["text"] = item_dictionary["text"] + [item]
                else :
                    item_dictionary["text"] = [item]
        return item_dictionary

if __name__ == '__main__':
    url = "http://127.0.0.1:4723/wd/hub"
    runner = DriverFactory(url, desired_caps)
    try :
        runner.crawl_app()
    except Exception as e:
        print(e)
        os.system('adb shell am force-stop com.citrix.Receiver')
        runner.driver.activate_app("com.citrix.Receiver")
        runner.crawl_app()
