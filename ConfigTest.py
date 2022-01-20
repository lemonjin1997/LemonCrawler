from bs4 import BeautifulSoup
import requests
import json
import datetime
from selenium import webdriver

class ConfigTest:
    def __init__(self, inputURL, configurationProfile):
        # Opening JSON file
        self.configrationData = {}
        self.inputURL = inputURL
        with open(configurationProfile) as json_file:
            self.configrationData = json.load(json_file)
        
            # Print the type of data variable
            #print("Type:", type(configrationData))
        
            # Print the data of dictionary
            #print(self.configrationData)
    

    def seleniumTool(self, configrationData, inputURL):
        #setup the webdriver in selenium tool
        driver = webdriver.Chrome(R'C:\Users\ASUS\Downloads\chromedriver_win32\chromedriver.exe', keep_alive=True)
        driver.get(inputURL)
        outputDic = {}
        print("setup webdriver")
        #time.sleep(10)
        
        
        for fieldConfiguration in configrationData.keys():
            
            title = configrationData[fieldConfiguration]['Title']
            print(title)
            selectionType = configrationData[fieldConfiguration]['SelectionType']
            print(selectionType)
            if selectionType == "xpath":
                xpath = configrationData[fieldConfiguration]['WebElementSelector']
                dataType = configrationData[fieldConfiguration]['DataType']
                outputDic[title] = self.xpathGetter(driver, xpath, dataType)
            if selectionType == "css selector":
                cssSelector = configrationData[fieldConfiguration]['WebElementSelector']
                dataType = configrationData[fieldConfiguration]['DataType']
                outputDic[title] = self.cssSelectorGetter(driver, cssSelector, dataType)
            if selectionType == 'select':
                tmpSoup = BeautifulSoup(driver.page_source, "html.parser")
                tag = configrationData[fieldConfiguration]['WebElementTag']
                classValue = configrationData[fieldConfiguration]['WebElementClass']
                dataType = configrationData[fieldConfiguration]['DataType']
                outputDic[title] = self.selectTagClass(tmpSoup, tag, classValue, dataType)
        return outputDic

    def requestTool(self, configrationData, inputURL):
        response = requests.get(inputURL, timeout=60, stream=True, headers={'User-Agent': "viscesa"})
        outputDic = {}
        tmpSoup = BeautifulSoup(response.content, "html.parser")

        for fieldConfiguration in configrationData.keys():
            print(fieldConfiguration)
            title = configrationData[fieldConfiguration]['Title']
            selectionType = configrationData[fieldConfiguration]['SelectionType']
            print(selectionType)
            if selectionType == "css selector":
                cssSelector = configrationData[fieldConfiguration]['WebElementSelector']
                dataType = configrationData[fieldConfiguration]['DataType']
                if dataType == "text":
                     outputDic[title] = tmpSoup.select_one(cssSelector).text
               
            if selectionType == 'select':
                tag = configrationData[fieldConfiguration]['WebElementTag']
                classValue = configrationData[fieldConfiguration]['WebElementClass']
                dataType = configrationData[fieldConfiguration]['DataType']
                outputDic[title] = self.selectTagClass(tmpSoup, tag, classValue, dataType)
        return outputDic



    def run(self):

        configrationData = self.configrationData
        print("Configuration Read: " + self.configrationData['ScarpingWebsiteSubString'])
        inputURL = self.inputURL
        # checking if the inputURL match the configuration's scarping website
        for x in range(len(configrationData['ScarpingWebsiteSubString'])-1):
            if inputURL[x] != configrationData['ScarpingWebsiteSubString'][x]:
                print("Error Scraping Website Mismatch")
                break
        configrationData.pop('ScarpingWebsiteSubString')

        # check the tool used by the configration....
        if configrationData['Tool'] == 'selenium':
            configrationData.pop('Tool')
            print(self.seleniumTool(configrationData, inputURL))
            return
        if configrationData['Tool'] == 'request':
            configrationData.pop('Tool')
            print(self.requestTool(configrationData, inputURL))

    def webElementGetter(self,webElement, typeSelector):
        if webElement is None or typeSelector is None:
            print("Error webElement")

        # Selector checks
        if typeSelector == "text":
            return webElement.text
        if typeSelector == "picture":
            rawHtml = webElement.get_attribute('outerHTML')
            pic_soup = BeautifulSoup(rawHtml, "html.parser")
            print(pic_soup.find('img')['src'])
            pic = requests.get(pic_soup.find('img')['src'])
            timeNow = datetime.datetime.now()
            tmpStamp = str(timeNow).replace(' ', '_').replace('.', '_').replace(':', '-')
            file = open(tmpStamp+".png", "wb")
            file.write(pic.content)
            file.close()
            return tmpStamp
        if typeSelector == "raw":
            return webElement.get_attribute('outerHTML')

    def xpathGetter(self, driver, xpath, typeSelector):
        # create web element
        webElement = driver.find_element_by_xpath(xpath)
        # empty check
        if xpath is None or driver is None or typeSelector is None:
            print("Error xpathGetter ")
        return self.webElementGetter(webElement, typeSelector)
        

    def cssSelectorGetter(self, driver, cssSelector, typeSelector):
        # empty check
        if cssSelector is None or driver is None or typeSelector is None:
            print("Error cssSelectorGetter ")
        # create web element
        webElement = driver.find_element_by_css_selector(cssSelector)
        return self.webElementGetter(webElement, typeSelector)

    def idGetter(self, driver, id, typeSelector):
        # empty check
        if id is None or driver is None or typeSelector is None:
            print("Error cssSelectorGetter ")

        # create web element
        webElement = driver.find_element_by_id(id)
        return self.webElementGetter(webElement, typeSelector)

    def selectTagClass(self, soup, tag, classValue, typeSelector):
        if soup is None or tag is None or classValue is None or typeSelector is None:
            print("Error selectTagClass")
            return
        webElement = soup.find(tag, class_=classValue)
        if typeSelector == "text":
            return webElement.text
        if typeSelector == "raw":
            return str(webElement)
        if typeSelector == "list":
            webElements = soup.find_all(tag, class_=classValue)
            text_list = []
            for webElement in webElements:
                text_list.append(webElement.text)
            return text_list


inputURL = "https://www.channelnewsasia.com/world/biden-says-any-russian-movement-ukraine-will-be-considered-invasion-2449066"
print("User's Crawled URL: " + inputURL)
configurationProfile = 'cnaProfile.json'
configTest = ConfigTest(inputURL, configurationProfile)
print(configTest.run())