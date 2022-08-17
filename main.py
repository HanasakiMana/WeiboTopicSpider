from argparse import Action
from tkinter import BROWSE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains



import csv
import datetime
from time import sleep
import time

# 全局变量
topic = '上海疫情 封城'
start_time = '2022-02-01-0'
stop_time = '2022-08-01-23'

# 以小时为单位拆分时间范围
time_list = []
start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d-%H")
stop_time = datetime.datetime.strptime(stop_time, "%Y-%m-%d-%H")
while start_time <= stop_time:
    date_str = start_time.strftime("%Y-%m-%d-%H")
    time_list.append(date_str)
    start_time += datetime.timedelta(hours=1)

# 声明webdriver
driver = webdriver.Chrome()

# 写入csv的第一行信息
file = open(f'{topic}.csv', 'w')
csvWriter = csv.writer(file)
csvWriter.writerow(['date','time', 'nickname', 'content'])
file.close()

# 爬
driver.get('https://m.weibo.com/login.php')
if input('请在登录后按下回车键:'):
    pass
else:
    driver.refresh()
    for k in range(0, len(time_list) - 1):
        # 获取当前时间段的开始时间和截止时间（跨度1小时）
        currentTime = time_list[k]
        nextTime = time_list[k+1]
        print(f'----------正在爬取：{currentTime}至{nextTime}----------')
        
        jumpOut = 0 # 一个flag，如果已经到了最后一页就会被置1，用于跳出循环
        for j in range(1, 51): # 微博最多展示50页搜索结果
            if jumpOut == 1:
                break

            driver.refresh()
            print(f'正在爬取第{j}页')
            link = f'https://s.weibo.com/weibo?q={topic}&scope=ori&suball=1&timescope=custom:{currentTime}:{nextTime}&Refer=g&page={j}' # 带高级搜索的请求
            data = [] # 保存爬取数据的列表

            driver.get(link) # 访问链接
            
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'from'))) # 等待元素加载
            contents = driver.find_elements(By.CLASS_NAME, 'txt') # 微博文本
            publishedFrom = driver.find_elements(By.CLASS_NAME, 'from') # 发布日期和设备
            
            # 展开被折叠的微博正文内容
            try:
                expand = driver.find_elements(By.CSS_SELECTOR, '#pl_feedlist_index > div:nth-child(2) > div > div > div.card-feed > div.content > p:nth-child(3) > a > i')
                handle = driver.current_window_handle # 获取当前操作的页面id，用于之后清除多余窗口
                for i in expand:
                    i.click()
                    sleep(1)
                # 清除掉因为点击多打开的窗口
                for newhandle in driver.window_handles:
                    if newhandle != handle:
                        driver.switch_to.window(newhandle)
                        driver.close()
                driver.switch_to.window(handle)
            except:
                pass
            # 对展开内容进行替换，摒弃未展开完全的内容，保留不需要展开的内容
            contents_full = []
            for content in contents:
                if content.text!= '':
                    contents_full.append(content)
            contents = contents_full
            # 验证是否出现无搜索结果的提示
            try:
                driver.find_element(By.XPATH, '//*[@id="pl_feedlist_index"]/div[3]/div/img') # 这个是提示没有搜索结果的图片
                print('找不到更多数据')
                break
            except:
                pass

            print(f'共找到{len(publishedFrom)}条微博')
            
            for i in range(0, len(publishedFrom)):
                card = contents[i]

                # 删除正文结尾因为展开留下的“收起”文本
                content = card.text.replace('\n', ' ')
                if content.split(' ')[-1] == '收起d': 
                    content = content[:-4]
                
                username = card.get_attribute('nick-name')
                publishedTime = publishedFrom[i].text.split(' ')

                # 对发布日期进行解析
                if publishedTime[0][0:2] == '今天':
                    date = datetime.datetime.now().strftime("%m月%d日")
                    time = publishedTime[0].split('今天')[-1]
                else:
                    date = publishedFrom[i].text.split(' ')[0]
                    time = publishedFrom[i].text.split(' ')[1]
                
                # 将数据append进列表
                data.append([date, time, username, f"'{content}'"])

            # 写入csv
            with open(f'{topic}.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            if j != 50:
                print('写入完成，等待爬取下一页')
                sleep(5)
            else:
                print('写入完成')