import base64
import subprocess
import re
from sys import platform
from apscheduler.schedulers.blocking import BlockingScheduler
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
        # 初始化机器人，扫码登陆

        receiver = bot.friends().search('何大')[0]
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])
        options.add_argument('disable-infobars')
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)
        driver.get("https://ss-ss.ooo/")
        wait = WebDriverWait(driver, 20, 0.2)
        # 循环遍历tr
        tr_num = 1
        ip_list = []
        ip_map = {}
        url_map = {}
        sleep(15)
        while tr_num < 36:
            tables = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
            print(tables[1].get_attribute("id"))
            global div_id
            div_id = tables[1].get_attribute("id")
            ip = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="'+div_id+'"]/tbody/tr[' + str(tr_num) + ']/td['
                                                                                                            '2]'))).text
            tr_num += 1
            print(ip)
            if platform == "linux" or platform == "darwin":
                out = subprocess.Popen(['ping', '-c', '5', ip], stdout=subprocess.PIPE)
                decode = out.stdout.read().decode()
                index = decode.index('/')
                print(decode[index + 1:index + 4] + ':' + decode[index + 26:index + 33])
                avg_time = float(decode[index + 26:index + 33])
            else:
                out = subprocess.Popen(['ping', '-n', '5', ip], stdout=subprocess.PIPE)
                decode = out.stdout.read().decode("gbk")
                avg_str = re.search("平均 = (\d+)", str(decode)).group()
                avg_time = float(avg_str[avg_str.index("=")+1:len(avg_str)].strip())

            ip_list.append(avg_time)
            get_png(wait, driver, ip_map, avg_time,url_map)
    except TimeoutException:
        print('===超时警告')
        pass
    finally:
        driver.close()
        if len(ip_list) == 0:
            print('未获取到页面元素')
            return
        print('最快的响应时间:' + str(min(ip_list)))
        print('最慢的响应时间:' + str(max(ip_list)))
        print(ip_map.keys())
        print(str(min(ip_list)))
        # 将二维码发送给接收人
        send_qrcode(receiver, ip_map[min(ip_list)], url_map[min(ip_list)], str(min(ip_list)))



"""
获取二维码
"""


def get_png(wait, driver, ip_map, avg_time,url_map):
    button = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="'+div_id+'"]/tbody/tr[1]/td[8]/i')))
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


def send_qrcode(receiver, png, url, avgTime):
    with open(r"new.png", 'wb') as f:
        f.write(png)
        f.close()
    receiver.send("此次最快响应时间:" + avgTime)
    receiver.send_image('new.png')
    receiver.send(url)
    print("最快url===============>"+url)


if __name__ == '__main__':
    try:
        scheduler = BlockingScheduler()
        scheduler.add_job(collect_fastest_ip, 'interval', seconds=300)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit, SystemError):
        print('===出错了')
        pass
