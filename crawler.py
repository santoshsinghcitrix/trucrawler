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


class DriverFactory() :

    visited_pages = []
    visited_items = []
    visited_page_source=[]
    blacklist = "Navigate Up"
    driver = None


    def __init__(self, url, desired_caps):
        self.driver = self.create_driver(url, desired_caps)

    def create_driver(self, url, desired_caps):
        return(webdriver.Remote(url, desired_caps))

    def quit_driver(self):
        self.driver.quit()

    def crawl_app(self):
        self.wait_for_load()
        start_activity = self.driver.current_activity
        print(self.driver.current_activity)
        start_page_source=self.driver.page_source
        print(self.visited_pages)
        if self.driver.current_activity not in self.visited_pages :
            self.visited_pages.append(self.driver.current_activity)
            self.visited_page_source.append(self.driver.page_source)
            if bool(re.search("WEBVIEW_com.citrix.Receiver", self.driver.contexts, re.IGNORECASE)) :
                current_context="WEBVIEW_com.citrix.Receiver"
                self.driver.switch_to.context(current_context)
                list_of_links = self.driver.find_elements_by_xpath("//a")
                list_of_inputs = self.driver.find_elements_by_xpath("//input")
                for item in list_of_inputs:
                    for text_to_enter in input_values.keys():
                        if bool(re.search(text_to_enter, str(item.get_attribute("name")) +
                                                         str(item.get_attribute("id")) +
                                                         str(item.text))):
                            item.send_keys(input_values[text_to_enter])
                for item in list_of_inputs:
                    print("++++++++++++++++++++++++++++++++++++++")
                    print("=======================================")
                    if item.is_enabled() \
                            and not bool(
                        re.search(str(item.get_attribute("id")), self.blacklist, re.IGNORECASE)) \
                            and item not in self.visited_items:
                        self.visited_items.append(item)
                        activity_name = self.driver.current_activity
                        prev_page_source = self.driver.page_source
                        item.click()
                        print("Clicking item")
                        # self.action_click(item)
                        try:
                            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(item))
                        except:
                            pass
                        EC.invisibility_of_element(item)
                        self.wait_for_load_buffer(prev_page_source)
                        # print(self.driver.page_source)
                        # if len(self.visited_page_source) >=2:
                        #     if self.driver.page_source == self.visited_page_source[-2] :
                        #         break
                        if prev_page_source != self.driver.page_source:
                            self.crawl_app()
                self.driver.switch_to.context("NATIVE_APP")

            else :
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
                        print(item.is_enabled())
                        print(bool(item.get_attribute("clickable")))
                        print(bool(re.search("button", str(item.get_attribute("class")), re.IGNORECASE)))
                        print("=======================================")
                        if item.is_enabled() \
                                and not bool(re.search(str(item.get_attribute("content-desc")), self.blacklist, re.IGNORECASE))\
                                and item not in self.visited_items:
                            self.visited_items.append(item)
                            print(item.get_attribute("class"))
                            print(item.get_attribute("text"))
                            activity_name = self.driver.current_activity
                            prev_page_source = self.driver.page_source
                            item.click()
                            print("Clicking item")
                            # self.action_click(item)
                            try:
                                WebDriverWait(self.driver, 10).until(EC.invisibility_of_element(item))
                            except:
                                pass
                            EC.invisibility_of_element(item)
                            self.wait_for_load_buffer(prev_page_source)
                            # print(self.driver.page_source)
                            # if len(self.visited_page_source) >=2:
                            #     if self.driver.page_source == self.visited_page_source[-2] :
                            #         break
                            if prev_page_source != self.driver.page_source :
                                self.crawl_app()

        if start_page_source != self.driver.page_source :
            print("Backing")
            self.driver.back()

    def previous_page_load(self, prev_page_source):
        while (bool(re.search("load", self.driver.page_source, re.IGNORECASE))
               or bool(re.search("spinner@", self.driver.page_source, re.IGNORECASE))
               or bool((not re.search("clickable=\"true\"", self.driver.page_source, re.IGNORECASE)))
               or bool(re.search("ProgressBar", self.driver.page_source, re.IGNORECASE))
               or prev_page_source == self.driver.page_source):
            time.sleep(1)

    def wait_for_load_buffer(self, prev_page_source):
        while (bool(re.search("load", self.driver.page_source, re.IGNORECASE))
               or bool(re.search("spinner@", self.driver.page_source, re.IGNORECASE))
               or bool((not re.search("clickable=\"true\"", self.driver.page_source, re.IGNORECASE)))
               or bool(re.search("ProgressBar", self.driver.page_source, re.IGNORECASE))
               or prev_page_source == self.driver.page_source):
            time.sleep(1)

    def wait_for_load(self):
        time.sleep(1)
        while (bool(re.search("load", self.driver.page_source, re.IGNORECASE))
               or bool(re.search("spinner@", self.driver.page_source, re.IGNORECASE))
               or bool((not re.search("clickable=\"true\"", self.driver.page_source, re.IGNORECASE)))
               or bool(re.search("ProgressBar", self.driver.page_source, re.IGNORECASE))):
            time.sleep(1)

    def identify_element(self, list_of_elements):
        # list_of_elements = self.driver.find_elements_by_xpath("//*")
        item_dictionary = {}
        for item in list_of_elements:
            if bool(re.search("EditText", str(item.get_attribute("class")), re.IGNORECASE)):
                if "input" in item_dictionary.keys():
                    item_dictionary["input"] = item_dictionary["input"] + [item]
                else :
                    item_dictionary["input"] = [item]
            elif (bool(re.search("button", str(item.get_attribute("class")), re.IGNORECASE))
                  or bool(re.search("button", str(item.get_attribute("class")), re.IGNORECASE)))\
                    and (str(item.get_attribute("text")) != ""
                         or str(item.get_attribute("text")) != "" ):
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

if __name__ == '__main__':
    url = "http://127.0.0.1:4723/wd/hub"
    runner = DriverFactory(url, desired_caps)
    try :
        runner.crawl_app()
    except Exception as e:
        print(e)
        runner.visited_pages.clear()
        runner.driver.back()
        # os.system('adb shell am force-stop com.citrix.Receiver')
        # runner.driver.terminate_app("com.citrix.Receiver")
        # runner.driver.activate_app("com.citrix.Receiver")
        runner.crawl_app()
