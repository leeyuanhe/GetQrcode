import base64
from apscheduler.schedulers.blocking import BlockingScheduler
from mping import mping
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from wxpy import *

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
        driver.get("https://free-ss.site")
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
        fastest_ip = resultList[0][0]
        min_avg = str(resultList[0][1].avg)
        print(fastest_ip+"======"+min_avg)
        tr_num = ip_map[fastest_ip]
        get_png(wait, driver, ip_map, min_avg,url_map,str(tr_num))
    except TimeoutException:
        print('===超时警告')
        pass
    finally:
        driver.close()
        if len(orgip_list) == 0:
            print('未获取到页面元素')
            return
        print("最快响应ip："+fastest_ip)
        # 将二维码发送给接收人
        send_qrcode(receiver, ip_map[min_avg], url_map[min_avg], min_avg)



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
        scheduler.add_job(collect_fastest_ip, 'interval', seconds=500)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit, SystemError):
        print('===出错了')
        pass
