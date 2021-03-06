import base64
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from mping import mping
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from wxpy import *
from time import sleep
# 初始化机器人，扫码登陆
bot = Bot(console_qr=False, cache_path=True)
dev_id = ''
"""
获取速度最快的IP地址
"""


def collect_fastest_ip():
    try:
        # 晚11:30 ~ 早08:00 不再推送
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        start = datetime.time(23, 30, 0)
        end = datetime.time(8, 0, 0)
        in_range = time_in_range(start, end, datetime.time(hour, minute, 0))
        if(not in_range):
            receiver = bot.friends().search('何大')[0]
            options = webdriver.ChromeOptions()
            # 设置为开发者模式，避免被识别
            options.add_experimental_option('excludeSwitches',
                                            ['enable-automation'])
            options.add_argument('disable-infobars')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            driver = webdriver.Chrome(options=options)
            driver.get("https://free-ss.site")
            sleep(20)
            wait = WebDriverWait(driver, 20, 0.2)
            # 循环遍历tr
            tr_num = 1
            orgip_list = []
            ip_map = {}
            url_map = {}
            tables = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
            print(tables[1].get_attribute("id"))
            global div_id
            div_id = tables[1].get_attribute("id")
            tbody = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="'+div_id+'"]/tbody')))
            elements = tbody.find_elements(By.TAG_NAME, "tr")
            for row in elements:
                ip = row.find_element_by_xpath(".//td[2]").text
                orgip_list.append(ip)
                ip_map[ip]=tr_num
                tr_num += 1
            resultList = mping(orgip_list)
            for tuplerow in range(5):
                fastest_ip = resultList[tuplerow][0]
                min_avg = str(resultList[tuplerow][1].avg)
                print(fastest_ip+"======"+min_avg)
                tr_num = ip_map[fastest_ip]
                get_png(wait, driver, ip_map, min_avg, url_map,str(tr_num))
                # 将二维码发送给接收人
                send_qrcode(receiver, ip_map[min_avg], url_map[min_avg], min_avg, tuplerow)
        else:
            print("==打烊了")
    except TimeoutException:
        print('===超时警告')
        pass
    finally:
        driver.close()
        if len(orgip_list) == 0:
            print('未获取到页面元素')
            return




"""
获取二维码
"""


def get_png(wait, driver, ip_map, avg_time,url_map,tr_num):
    button = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="'+div_id+'"]/tbody/tr['+tr_num+']/td[8]/i')))
    button.click()
    canvas = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="qrcode"]/canvas')))
    href_element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'URI')))
    print(href_element.get_attribute('href'))
    ss_url = href_element.get_attribute('href')
    # get the canvas as a PNG base64 string
    canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
    # decode
    canvas_png = base64.b64decode(canvas_base64)
    ip_map[avg_time] = canvas_png
    url_map[avg_time] = ss_url
    button = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'layui-layer-shade')))
    driver.execute_script("arguments[0].click()", button)


"""
发送二维码到微信
"""


def send_qrcode(receiver, png, url, avgTime, index):
    with open(r"new.png", 'wb') as f:
        f.write(png)
        f.close()
    receiver.send("第"+str(index+1)+"名最快响应时间:" + avgTime)
    receiver.send_image('new.png')
    receiver.send(url)
    print("最快url===============>"+url)

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


if __name__ == '__main__':
    try:
        scheduler = BlockingScheduler()
        scheduler.add_job(collect_fastest_ip, 'interval', seconds=300)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit, SystemError):
        print('===出错了')
        pass
