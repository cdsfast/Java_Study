# coding=utf-8
__author__ = 'lixuefang'

import time
import unittest
from appium import webdriver
import os
import datetime
from PublicUtils.public_functions import writeDateToFile, appium_start
from ConfigInfo import baseConfig

class SearchTest(unittest.TestCase):

    def setUp(self):
        self.driver = appium_start()

        xy = self.driver.get_window_size()
        self.x = xy['width']
        self.y = xy['height']

    def tearDown(self):
        os.system("ps -ef | grep get_cpu_memory_v3 | grep -v grep | awk '{print $2}' | xargs kill -9")
        self.driver.quit()

    def test_case(self):
        driver = self.driver
        time.sleep(20)
        # 步骤A
        timeA = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i in range(2):
            driver.swipe(0.5 * self.x, 0.9 * self.y, 0.5 * self.x, 0.1 * self.y, 1000)
            time.sleep(3)
        # 步骤B
        timeB = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timeData = timeA + ',' + timeB
        # 将A 和 B 的时间用逗号连起来后，存储到相应的case文件中
        timeFile = os.getcwd() + baseConfig['case5']['directory'] + '/' + baseConfig['case5']['time_file']
        writeDateToFile(timeData, timeFile)


if __name__ == '__main__':
    unittest.main()

