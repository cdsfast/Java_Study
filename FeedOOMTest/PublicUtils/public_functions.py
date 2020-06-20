# coding=utf-8

__author__ = 'lixuefang'

from appium import webdriver
import shutil
import os
import warnings


def appium_start():
    platformVersion = os.popen('adb shell getprop ro.build.version.release')
    deviceName = os.popen('adb devices')

    desired_caps = {}
    desired_caps['platformName'] = 'Android'  # 使用哪个移动操作系统平台
    desired_caps['platformVersion'] = platformVersion.read()   # 移动操作系统版本
    desired_caps['deviceName'] = deviceName.read()  # 手机序列号
    # desired_caps['platformVersion'] = '7'  # 移动操作系统版本
    # desired_caps['deviceName'] = '03157df35372480b'  # 手机序列号
    # desired_caps['app'] = os.path.dirname(os.getcwd()) + '\\App\\searchbox.apk'
    desired_caps['unicodeKeyboard'] = True
    desired_caps['resetKeyboard'] = True
    desired_caps['fullReset'] = False
    desired_caps['noReset'] = True
    desired_caps['recreateChromeDriverSessions'] = True
    desired_caps['newCommandTimeout'] = 1000  # Appium等待来自客户端的新命令时间（以秒为单位）
    desired_caps['appPackage'] = 'com.baidu.searchbox'
    desired_caps['appActivity'] = '.MainActivity'

    platformVersion.close()  # 关闭文件
    deviceName.close()  # 关闭文件
    warnings.simplefilter('ignore', 'ResourceWarning')  # 忽略ResourceWarning报错

    driver = webdriver.Remote('http://0.0.0.0:4723/wd/hub', desired_caps)
    return driver
    # 这里init应该进入到对应的页面哦～

# 判断文件夹是否存在，如果存在，删除文件夹后再重新创建
def dirIsExist(durarionpath):
    flag = os.path.exists(durarionpath)
    if flag:
        shutil.rmtree(durarionpath)
    os.makedirs(durarionpath)


# 判断文件是否存在，如果存在，删除文件后再重新创建
def fileIsExist(filepath):
    flag = os.path.exists(filepath)
    if flag:
        os.remove(filepath)


def writeDateToFile(timeData, path):
    with open(path, "a") as file:
        file.writelines(str(timeData) + '\n')
