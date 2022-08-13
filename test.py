from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep

driver = webdriver.Chrome()
action_chains = ActionChains(driver)

driver.get('https://s.weibo.com/weibo?q=%E4%B8%8A%E6%B5%B7%E7%96%AB%E6%83%85%20%E5%B0%81%E5%9F%8E')
sleep(5)
action_chains.send_keys(Keys.COMMAND, 'w').perform()
print(1)