#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
#
################################################################################


import os
import time
import re
import argparse

class baseClass(object):
    '''基础数据类'''

    def __init__(self, phone_id, PACKAGE_NAME):
        self.phone_id = phone_id
        self.PACKAGE_NAME = PACKAGE_NAME

        self.MAX_INVALID_LINE = 5
        self.KEYWORD_TOP_CPU = "CPU%"
        self.KEYWORD_TOP_PID = "PID"
        self.KEYWORD_TOP_RSS = "RSS"
        self.KEYWORD_TOP_VSS = "VSS"

        self.KEYWORD_MEMINFO_PID = "pid"
        self.KEYWORD_MEMINFO_NATIVE = 'Native'
        self.KEYWORD_MEMINFO_DALVIK = 'Dalvik'
        self.KEYWORD_MEMINFO_TOTAL = 'TOTAL'
        self.KEYWORD_MEMINFO_PSS = 'PSS'

    def dump_init_top(self):
        '''初始化top信息'''
        print("------------adb shell top -n 1------------")
        topDict = dict()
        ret = 0
        if self.phone_id != "":
            ret = os.popen("adb -s " + self.phone_id + " shell top -n 1")
        else:
            ret = os.popen("adb shell top -n 1")
        while True:
            title = ret.readline()
            # if ret.readline():
            if "USER" in title and "MEM" in title:
                #  PID USER         PR  NI VIRT  RES  SHR S[%CPU] %MEM     TIME+ ARGS
                tab_data = re.match(r".+\s+[A-Z]\W?(?P<key>%cpu)\W?.+", str(title), re.I)
                topDict["CPU"] = tab_data.group("key")
                print("Get CPU Signal: ", topDict["CPU"])
                break
            if "VSS" in title and "RSS" in title:
                #  PID PR CPU% S  #THR     VSS     RSS PCY UID      Name
                tab_data = re.match(r".+\s+?(?P<key>CPU%)\s+[A-Z]\s+.+", str(title), re.I)
                topDict["CPU"] = tab_data.group("key")
                print("Get CPU Signal: ", topDict["CPU"])
                break

    def dump_init_meminfo(self):
        '''初始化dump memory info'''
        print("-------------adb shell meminfo------------")
        memDict = dict()
        ret = self.dump_execute_meminfo()
        i = 0
        while True:
            i = i + 1
            line = str(ret.readline())
            if not 'No process found for' in line and not len(line) == 0:
                title = line.split()
                if self.KEYWORD_MEMINFO_PID in title:
                    memDict["PID"] = title.index(self.KEYWORD_MEMINFO_PID)
                    print("Get PID Signal: ", title[memDict["PID"]])
                elif self.KEYWORD_MEMINFO_NATIVE in line and 'Heap' in line:
                    memDict["NATIVE"] = title.index(self.KEYWORD_MEMINFO_NATIVE)
                    print("Get NATIVE HEAP Signal: ", title[memDict["NATIVE"]])
                elif self.KEYWORD_MEMINFO_DALVIK in line and 'Heap' in line:
                    memDict["DALVIK"] = title.index(self.KEYWORD_MEMINFO_DALVIK)
                    print("Get DALVIK HEAP Signal: ", title[memDict["DALVIK"]])
                elif self.KEYWORD_MEMINFO_TOTAL in line:
                    memDict["PSS"] = title.index(self.KEYWORD_MEMINFO_TOTAL)
                    print("Get PSS Signal: ", title[memDict["PSS"]])
                    print("------------------memDict------------------")
                    break
            elif i < self.MAX_INVALID_LINE:
                continue
            else:
                print("can't connect to devices")
                time.sleep(5)
                ret = self.dump_execute_meminfo()
                i = 0

    def dump_get_meminfo_line(self):
        '''获取单条数据data'''
        titles = []
        ret = self.dump_execute_meminfo()
        for title in ret.readlines():
            if 'No process found' in title or len(title) == 0:
                break
            line = title.split()
            if self.KEYWORD_MEMINFO_PID in line:
                titles.append(line[4])
            elif self.KEYWORD_MEMINFO_NATIVE in line and 'Heap' in line:
                titles.append(line[-2])
            elif self.KEYWORD_MEMINFO_DALVIK in line and 'Heap' in line:
                titles.append(line[-2])
            elif self.KEYWORD_MEMINFO_TOTAL in line:
                titles.append(line[1])
                break
        return titles

    def dump_get_top(self):
        '''获取单条数据data  cpu'''
        cpu_data = "  "
        if self.phone_id != "":
            ret = os.popen("adb -s " + self.phone_id + " shell top -n 1")
        else:
            ret = os.popen("adb shell top -n 1")
        for title in ret.readlines():
            if re.match(r".+com.baidu.searchbox\s+?$", title, re.I) != None:  # 低版本手机
                # 15561  3  10% S   208 2408416K 445800K  tv u0_a120  com.baidu.searchbox
                data = re.match(r"^.+\d+\s+?(?P<key>\d+%)\s+?[A-Z]\s+\d+\s.+com.baidu.searchbox\s+?$", title, re.I)
                cpu_data = data.group(1)
                break
            if re.match(r".+com.baidu.se[a-zA-Z]+?\+\s+?$", title, re.I) != None:  # 高版本手机
                # 31603 u0_a207      19  -1 2.3G 405M 199M R 60.0   7.0   2:37.25 com.baidu.searc+
                data = re.match(
                    r".+\d+[A-Z]\s+[A-Z]\s+?(?P<key>\d+\W?\d+)\s+\d+\W?\d+\s+.+com.baidu.se[a-zA-Z]+?\+\s+?$", title,
                    re.I)
                cpu_data = data.group("key")
                break
        return cpu_data

    def dump_execute_meminfo(self):
        '''获取命令行所有数据'''
        ret = 0
        if self.phone_id != '':
            ret = os.popen("adb -s " + self.phone_id + " shell dumpsys meminfo " + self.PACKAGE_NAME)
        return ret

    def top_init_top(self):
        '''初始化top信息'''
        print("-------------adb shell top -n 1------------")
        topDict = dict()
        ret = None
        if self.phone_id != "":
            ret = os.popen("adb -s " + self.phone_id + " shell top -n 1")
        else:
            ret = os.popen("adb shell top -n 1")
        while True:
            title = ret.readline().split()
            if self.KEYWORD_TOP_PID in title:
                topDict["CPU"] = title.index(self.KEYWORD_TOP_CPU)
                print("Get CPU Signal: ", title[topDict["CPU"]])
                topDict["PID"] = title.index(self.KEYWORD_TOP_PID)
                print("Get PID Signal: ", title[topDict["PID"]])
                topDict["RSS"] = title.index(self.KEYWORD_TOP_RSS)
                print("Get RSS Signal: ", title[topDict["RSS"]])
                topDict["VSS"] = title.index(self.KEYWORD_TOP_VSS)
                print("Get VSS Signal: ", title[topDict["VSS"]])
                print("------------topDict------------")
                break
        return topDict

    def top_get_top_line(self):
        '''获取单条数据data'''
        if self.phone_id != "":
            ret = os.popen("adb -s " + self.phone_id + " shell top -n 1")
        else:
            ret = os.popen("adb shell top -n 1")
        for title in ret.readlines():
            title = title.split()
            if self.PACKAGE_NAME in title and ':' not in title and '.selendroid' not in title:
                break
        return title

    def get_time(self):
        '''获取时间戳'''
        return time.strftime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


class topGetMemInfo(baseClass):
    # 此类使用adb shell top命令采集，他可以提供PID,CPU,VSS,RSS四种数据
    # 缺点：adb shell top命令运行一次的时间比较久，会延长循环间隔
    # 注意：使用于低版本ROM机器 8.0及以下的

    def __init__(self, phone_id, PACKAGE_NAME, PRINT_OR_WRITE='meanwhile', WAIT_TIME=0.5):
        # PRINT_OR_WRITE 默认值meanwhile-->写入文件并打印
        #                     print-->只打印，不写入文件
        #                     write-->只写入文件，不打印
        super(topGetMemInfo, self).__init__(phone_id, PACKAGE_NAME)
        self.WAIT_TIME = WAIT_TIME
        self.PRINT_OR_WRITE = PRINT_OR_WRITE
        self.KEYWORD_TOP_TIME = "TIME"

        time_stamp = time.strftime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
        self.result_file_name = self.phone_id[0:3] + "_top_mem_report_" + time_stamp + ".csv"

    def top_only(self):
        '''主方法'''
        topDict = baseClass.top_init_top(self)
        if self.PRINT_OR_WRITE == 'write' or self.PRINT_OR_WRITE == 'meanwhile':
            self.write_info(
                self.KEYWORD_TOP_PID + "," + self.KEYWORD_TOP_CPU + "," + self.KEYWORD_TOP_RSS + "," + self.KEYWORD_TOP_VSS + "," + self.KEYWORD_TOP_TIME)
        if self.PRINT_OR_WRITE == 'print':
            pass
        while True:
            data = baseClass.top_get_top_line(self)
            if self.PACKAGE_NAME in data:
                bufferLine = data[topDict["PID"]] + "," + data[topDict["CPU"]] + "," + data[topDict["RSS"]] + "," + \
                             data[topDict["VSS"]] + "," + baseClass.get_time(self)
                bufferLine = bufferLine.replace('K', '')
                if self.PRINT_OR_WRITE == 'meanwhile':
                    self.write_info(bufferLine)
                    print("[ "
                          + self.KEYWORD_TOP_PID + ': ' + data[topDict["PID"]] + " ]  [ "
                          + self.KEYWORD_TOP_CPU + ': ' + data[topDict["CPU"]] + " ]  [ "
                          + self.KEYWORD_TOP_RSS + ': ' + data[topDict["RSS"]] + " ]  [ "
                          + self.KEYWORD_TOP_VSS + ': ' + data[topDict["VSS"]] + " ]  [ "
                          + self.KEYWORD_TOP_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
                if self.PRINT_OR_WRITE == 'write':
                    self.write_info(bufferLine)
                if self.PRINT_OR_WRITE == 'print':
                    print("[ "
                          + self.KEYWORD_TOP_PID + ': ' + data[topDict["PID"]] + " ]  [ "
                          + self.KEYWORD_TOP_CPU + ': ' + data[topDict["CPU"]] + " ]  [ "
                          + self.KEYWORD_TOP_RSS + ': ' + data[topDict["RSS"]] + " ]  [ "
                          + self.KEYWORD_TOP_VSS + ': ' + data[topDict["VSS"]] + " ]  [ "
                          + self.KEYWORD_TOP_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
            # else:
                # print("wait app start ", baseClass.get_time(self))
                # self.write_info("wait app start " + baseClass.get_time(self))
            time.sleep(self.WAIT_TIME)

    def write_info(self, context):
        '''写数据到文件'''
        with open(self.result_file_name, "a") as report:
            report.write(context + "\n")
        report.close()


class dumpsysMemInfo(baseClass):
    # 此类调用adb shell dumpsys meminfo 命令采集内存数据
    # 以及adb shell top 采集CPU信息
    # 注意：已适配所有ROM机器

    def __init__(self, phone_id, PACKAGE_NAME, PRINT_OR_WRITE='meanwhile', WAIT_TIME=0.5):
        # PRINT_OR_WRITE 默认值meanwhile-->写入文件并打印
        #                     print-->只打印，不写入文件
        #                     write-->只写入文件，不打印
        super(dumpsysMemInfo, self).__init__(phone_id, PACKAGE_NAME)
        self.WAIT_TIME = WAIT_TIME
        self.PRINT_OR_WRITE = PRINT_OR_WRITE
        self.KEYWORD_MEMINFO_TIME = "TIME"

        time_stamp = time.strftime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
        self.result_file_name = self.phone_id[0:3] + "_dump_mem_report_" + time_stamp + ".csv"

    def mem_only(self):
        '''主方法，dump memory info 仅获取内存信息，没有包含CPU信息'''
        baseClass.dump_init_meminfo(self)
        if self.PRINT_OR_WRITE == 'write' or self.PRINT_OR_WRITE == 'meanwhile':
            self.write_info(
                self.KEYWORD_MEMINFO_PID + "," + self.KEYWORD_MEMINFO_NATIVE + "," + self.KEYWORD_MEMINFO_DALVIK + "," + self.KEYWORD_MEMINFO_PSS + "," + self.KEYWORD_MEMINFO_TIME)
        if self.PRINT_OR_WRITE == 'print':
            pass
        while True:
            data = baseClass.dump_get_meminfo_line(self)
            # if len(data) < 4:
                # print("wait app start ", baseClass.get_time(self))
                # self.write_info("wait app start " + baseClass.get_time(self))
            # else:
            if len(data) >= 5:
                bufferLine = data[0] + "," + data[1] + "," + data[2] + "," + data[3] + "," + baseClass.get_time(self)
                if self.PRINT_OR_WRITE == 'meanwhile':
                    self.write_info(bufferLine)
                    print("[ "
                          + self.KEYWORD_MEMINFO_PID + ': ' + data[0] + " ]  [ "
                          + self.KEYWORD_MEMINFO_NATIVE + ': ' + data[1] + " ]  [ "
                          + self.KEYWORD_MEMINFO_DALVIK + ': ' + data[2] + " ]  [ "
                          + self.KEYWORD_MEMINFO_PSS + ': ' + data[3] + " ]  [ "
                          + self.KEYWORD_MEMINFO_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
                if self.PRINT_OR_WRITE == 'write':
                    self.write_info(bufferLine)
                elif self.PRINT_OR_WRITE == 'print':
                    print("[ "
                          + self.KEYWORD_MEMINFO_PID + ': ' + data[0] + " ]  [ "
                          + self.KEYWORD_MEMINFO_NATIVE + ': ' + data[1] + " ]  [ "
                          + self.KEYWORD_MEMINFO_DALVIK + ': ' + data[2] + " ]  [ "
                          + self.KEYWORD_MEMINFO_PSS + ': ' + data[3] + " ]  [ "
                          + self.KEYWORD_MEMINFO_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
            time.sleep(self.WAIT_TIME)

    def tp_both(self):
        '''主方法，dump memory info 获取内存信息加top方法获取CPU信息'''
        baseClass.dump_init_top(self)
        baseClass.dump_init_meminfo(self)
        if self.PRINT_OR_WRITE == 'write' or self.PRINT_OR_WRITE == 'meanwhile':
            self.write_info(
                self.KEYWORD_MEMINFO_PID + "," + self.KEYWORD_MEMINFO_NATIVE + "," + self.KEYWORD_MEMINFO_DALVIK + "," + self.KEYWORD_MEMINFO_PSS + "," + self.KEYWORD_TOP_CPU + "," + self.KEYWORD_MEMINFO_TIME)
        if self.PRINT_OR_WRITE == 'print':
            pass
        while True:
            dataM = baseClass.dump_get_meminfo_line(self)
            dataT = baseClass.dump_get_top(self)
            if len(dataM) < 4:
                print("wait app start ", baseClass.get_time(self))
                # self.write_info("wait app start " + baseClass.get_time(self))
            elif dataT:
                bufferLine = dataM[0] + "," + dataM[1] + "," + dataM[2] + "," + dataM[
                    3] + "," + dataT + "," + baseClass.get_time(self)
                if self.PRINT_OR_WRITE == 'meanwhile':
                    self.write_info(bufferLine)
                    print("[ "
                          + self.KEYWORD_MEMINFO_PID + ': ' + dataM[0] + " ]  [ "
                          + self.KEYWORD_MEMINFO_NATIVE + ': ' + dataM[1] + " ]  [ "
                          + self.KEYWORD_MEMINFO_DALVIK + ': ' + dataM[2] + " ]  [ "
                          + self.KEYWORD_MEMINFO_PSS + ': ' + dataM[3] + " ]  [ "
                          + self.KEYWORD_TOP_CPU + ': ' + dataT + " ]  [ "
                          + self.KEYWORD_MEMINFO_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
                if self.PRINT_OR_WRITE == 'write':
                    self.write_info(bufferLine)
                elif self.PRINT_OR_WRITE == 'print':
                    print("[ "
                          + self.KEYWORD_MEMINFO_PID + ': ' + dataM[0] + " ]  [ "
                          + self.KEYWORD_MEMINFO_NATIVE + ': ' + dataM[1] + " ]  [ "
                          + self.KEYWORD_MEMINFO_DALVIK + ': ' + dataM[2] + " ]  [ "
                          + self.KEYWORD_MEMINFO_PSS + ': ' + dataM[3] + " ]  [ "
                          + self.KEYWORD_TOP_CPU + ': ' + dataT + " ]  [ "
                          + self.KEYWORD_MEMINFO_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
            time.sleep(self.WAIT_TIME)

    def write_info(self, context):
        '''写数据到文件'''
        with open(self.result_file_name, "a") as report:
            report.write(context + "\n")
        report.close()


class complexMemInfo(baseClass):
    # 综合类：获取VSS RSS PSS NATIVE JAVA CPU 等所有数据
    # 注意：仅适配底ROM机器 8.0及以下的

    def __init__(self, phone_id, PACKAGE_NAME, PRINT_OR_WRITE='meanwhile', WAIT_TIME=0.5):
        super(complexMemInfo, self).__init__(phone_id, PACKAGE_NAME)
        super(complexMemInfo, self).__init__(phone_id, PACKAGE_NAME)
        self.WAIT_TIME = WAIT_TIME
        self.PRINT_OR_WRITE = PRINT_OR_WRITE
        self.KEYWORD_MEMINFO_TIME = "TIME"

        time_stamp = time.strftime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
        self.result_file_name = self.phone_id[0:3] + "_mem_report_" + time_stamp + ".csv"

    def get_data_only(self, pathdir):
        # 主方法，获取综合数据

        # baseClass.dump_init_top(self)
        baseClass.dump_init_meminfo(self)
        topDict = baseClass.top_init_top(self)
        if self.PRINT_OR_WRITE == 'write' or self.PRINT_OR_WRITE == 'meanwhile':
            self.write_info(pathdir, self.KEYWORD_TOP_PID + "," + self.KEYWORD_TOP_CPU + "," + self.KEYWORD_TOP_RSS + ","
                            + self.KEYWORD_TOP_VSS + "," + self.KEYWORD_MEMINFO_NATIVE + "," + self.KEYWORD_MEMINFO_DALVIK + ","
                            + self.KEYWORD_MEMINFO_PSS + "," + self.KEYWORD_MEMINFO_TIME)

        if self.PRINT_OR_WRITE == 'print':
            pass
        while True:
            data = baseClass.top_get_top_line(self)
            dataM = baseClass.dump_get_meminfo_line(self)
            # dataT = baseClass.dump_get_top(self)
            if len(dataM) < 4:
                print("wait app start ", baseClass.get_time(self))
                # self.write_info(pathdir, "wait app start " + baseClass.get_time(self))
            elif self.PACKAGE_NAME in data:
                top_buffer = data[topDict["PID"]] + "," + data[topDict["CPU"]] + "," + data[topDict["RSS"]] + "," \
                             + data[topDict["VSS"]]
                top_bufferLine = top_buffer.replace('K', '')
                mem_bufferLine = "," + dataM[1] + "," + dataM[2] + "," + dataM[3] + "," + baseClass.get_time(self)
                bufferLine = top_bufferLine + mem_bufferLine

                if self.PRINT_OR_WRITE == 'meanwhile':
                    # self.write_info(bufferLine)
                    self.write_info(pathdir, bufferLine)

                    print("[ "
                          + self.KEYWORD_TOP_PID + ': ' + data[topDict["PID"]] + " ]  [ "
                          + self.KEYWORD_TOP_CPU + ': ' + data[topDict["CPU"]] + " ]  [ "
                          + self.KEYWORD_TOP_RSS + ': ' + data[topDict["RSS"]] + " ]  [ "
                          + self.KEYWORD_TOP_VSS + ': ' + data[topDict["VSS"]] + " ]  [ "
                          + self.KEYWORD_MEMINFO_NATIVE + ': ' + dataM[1] + " ]  [ "
                          + self.KEYWORD_MEMINFO_DALVIK + ': ' + dataM[2] + " ]  [ "
                          + self.KEYWORD_MEMINFO_PSS + ': ' + dataM[3] + " ]  [ "
                          + self.KEYWORD_MEMINFO_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
                if self.PRINT_OR_WRITE == 'write':
                    # self.write_info(bufferLine)
                    self.write_info(pathdir, bufferLine)

                if self.PRINT_OR_WRITE == 'print':
                    print("[ "
                          + self.KEYWORD_TOP_PID + ': ' + data[topDict["PID"]] + " ]  [ "
                          + self.KEYWORD_TOP_CPU + ': ' + data[topDict["CPU"]] + " ]  [ "
                          + self.KEYWORD_TOP_RSS + ': ' + data[topDict["RSS"]] + " ]  [ "
                          + self.KEYWORD_TOP_VSS + ': ' + data[topDict["VSS"]] + " ]  [ "
                          + self.KEYWORD_MEMINFO_NATIVE + ': ' + dataM[1] + " ]  [ "
                          + self.KEYWORD_MEMINFO_DALVIK + ': ' + dataM[2] + " ]  [ "
                          + self.KEYWORD_MEMINFO_PSS + ': ' + dataM[3] + " ]  [ "
                          + self.KEYWORD_MEMINFO_TIME + ": " + baseClass.get_time(self) + " ]"
                          )
            time.sleep(self.WAIT_TIME)

    def write_info(self, pathdir, context):
        # pathdir = '/Users/lixuefang/FeedOOMTest/Test02/'
        '''写数据到文件'''
        # report = open(self.result_file_name,"a")
        with open(pathdir + self.result_file_name, "a") as report:
            report.write(context + "\n")
        report.close()


def arg():
    # 命令行解析器
    # -d 设备id
    # -p 测试应用包名，默认值：com.baidu.searchbox
    # -w 数据存储方式，print或者write，默认值既打印又写文件
    # -h 帮助文档
    parse = argparse.ArgumentParser(usage='This script is mainly used to get performance data \n 此脚本主要用于获取性能数据',
                                    description='Devices is required, and the package name (the default is Baidu APP) \n 需传参设备devices，包名（默认是百度APP)')
    parse.add_argument('-d', help='devices', type=str, nargs='?', default=None)
    parse.add_argument('-p', help='package name', type=str, nargs='?', default=None)
    parse.add_argument('-w', help='print or write, Please input "print" or "write" or empty', type=str, nargs='?',
                       default=None)
    parse.add_argument('-c', help='path of write data', type=str, nargs='?', default=None)
    args = parse.parse_args()
    # print vars(args)
    return args


def initParameters():
    global DEVICE_ID, PACKAGE_NAME, PRINT_OR_WRITE, PATH_DIR

    args = arg()
    # 自动获取手机设备的序列号
    content = os.popen("adb devices").read()

    if args.d != None:  # devices
        DEVICE_ID = args.d
    if args.d == None:
        DEVICE_ID = content.split()[4]

    if args.p != None:  # 包名
        PACKAGE_NAME = args.p
    if args.p == None:  # 包名
        PACKAGE_NAME = 'com.baidu.searchbox'

    if args.w == None:
        PRINT_OR_WRITE = 'meanwhile'
    if args.w != None:
        if args.w == 'print':
            PRINT_OR_WRITE = 'print'
        if args.w == 'write':
            PRINT_OR_WRITE = 'write'
        else:
            print('-w input error !!!')
    else:
        pass
    if args.c != None: # 存储数据目录
        PATH_DIR = args.c
    else:
        PATH_DIR = os.getcwd() + '/'

# 调用runGetData方法，可获取性能数据
def runGetData(pathDir):
    # 1.初始化参数
    initParameters()
    print('pathdir:' + pathDir)
    # 调用方法2：通过meminfo获取NATIVE DALVIK PSS内存数据
    info = complexMemInfo(DEVICE_ID, PACKAGE_NAME, PRINT_OR_WRITE, WAIT_TIME=0.5)
    info.get_data_only(pathDir + '/')

# 主函数
# 运行脚本示例： python get_cpu_memory_v2.0.py -d QDYNW17C27006959
if __name__ == "__main__":
    # 1.初始化参数
    initParameters()

    # 2.启动性能数据抓取

    # 调用方法1：通过top获取CPU、RSS、VSS数据
    # 注意：仅适配Android ROM 8.0及以下的设备
    # info = topGetMemInfo(DEVICE_ID,PACKAGE_NAME, PRINT_OR_WRITE='meanwhile', WAIT_TIME=0.5)
    # info.top_only()

    # 调用方法2：通过meminfo获取NATIVE DALVIK PSS内存数据
    # 说明：已适配所有Android ROM设备
    # info = dumpsysMemInfo(DEVICE_ID,PACKAGE_NAME, PRINT_OR_WRITE='meanwhile', WAIT_TIME=0.5)
    # info.mem_only()

    # 调用方法3：综合以上两种方法，获取CPU、RSS、VSS、NATIVE DALVIK PSS全部性能数据
    # 注意：仅适配Android ROM 8.0及以下的设备

    # # 自动获取手机设备的序列号
    # content = os.popen("adb devices").read()
    # DEVICE_ID = content.split()[4]
    # pathDir = os.getcwd() + '/'
    info = complexMemInfo(DEVICE_ID, PACKAGE_NAME, PRINT_OR_WRITE, WAIT_TIME=0.5)
    info.get_data_only(PATH_DIR)


