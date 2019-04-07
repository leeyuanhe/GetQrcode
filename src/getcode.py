import base64
import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from wxpy import *

# 初始化机器人，扫码登陆
bot = Bot(console_qr=False, cache_path=True)

"""
获取速度最快的IP地址
"""


def collect_fastest_ip():
    try:
        # 初始化机器人，扫码登陆
        bot = Bot(console_qr=False, cache_path=True)
        receiver = bot.friends().search('何大')[0]

        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])
        options.add_argument('disable-infobars')
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)
        driver.get("https://xxxxxx.ooo/")
        wait = WebDriverWait(driver, 20, 0.2)
        # 循环遍历tr
        tr_num = 1
        ip_list = []
        ip_map = {}
        while tr_num < 36:
            ip = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tb0a3e"]/tbody/tr[' + str(tr_num) + ']/td[2]'))).text
            tr_num += 1
            print(ip)
            out = subprocess.Popen(['ping', '-c', '3', ip], stdout=subprocess.PIPE)
            decode = out.stdout.read().decode()
            index = decode.index('/')
            print(decode[index + 1:index + 4] + ':' + decode[index + 26:index + 33])
            avg_time = float(decode[index + 26:index + 33])
            ip_list.append(avg_time)
            get_png(wait, driver, ip_map, avg_time)
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
        # 将二维码发送给接收人
        send_qrcode(receiver, ip_map[min(ip_list)])



"""
获取二维码
"""


def get_png(wait, driver, ip_map, avg_time):
    button = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="tb0a3e"]/tbody/tr[1]/td[8]/i')))
    button.click()
    canvas = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="qrcode"]/canvas')))
    href_element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'URI')))
    print(href_element.get_attribute('href'))
    # get the canvas as a PNG base64 string
    canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
    # decode
    canvas_png = base64.b64decode(canvas_base64)
    ip_map[avg_time] = canvas_png
    button = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'layui-layer-shade')))
    driver.execute_script("arguments[0].click()", button)


"""
发送二维码到微信
"""


def send_qrcode(receiver, object):
    with open(r"new.png", 'wb') as f:
        f.write(object)
        f.close()
    receiver.send_image('new.png')


if __name__ == '__main__':
    try:
        scheduler = BlockingScheduler()
        scheduler.add_job(collect_fastest_ip, 'interval', seconds=300)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit, SystemError):
        print('===出错了')
        pass
