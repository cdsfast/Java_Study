# coding=utf-8
__author__ = 'lixuefang'
"""
之前单计算和生成最大值的脚本，目前已不用。
"""

import ConfigInfo
from ConfigInfo import maxCompareData
import pandas as pd
import glob
import os
import time
import xlsxwriter


def compareValue(listValue, avgValue, standardValue):
    """
    判断峰值的list和均值是否否小于给定的阈值，如果全都小于，则Pass，否则Fail
    :param listValue:  峰值的list值
    :param avgValue: 峰值的均值
    :param standardValue: 给定的阈值
    :return:
    """
    flag = 'Pass'
    for item in listValue:
        if item >= standardValue * 1024 * 1024:
            flag = 'Fail'
            break
    if avgValue >= standardValue:
        flag = 'Fail'
    return flag


def remove_percentile(col_data, column_data):
    """
    去除list col_data中元素的百分号，并将结果追加到新的列表column_data中
    :return:
    """
    for item in col_data:
        if '%' in str(item):
            item = item.strip('%')
        item = float(item)
        column_data.append(item)

time_stamp = time.strftime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
# 创建要生成的报告result.xlsx
workBook = xlsxwriter.Workbook('../Report/MaxResultReport' + time_stamp + '.xlsx')
worksheet = workBook.add_worksheet()


def setTitleStyle(font_color, font_size, bold, fg_color, align, valign):
    """
    设置生成表格的样式
    :param font_color: 字体颜色
    :param font_size: 字体大小
    :param bold: 字体加粗
    :param fg_color: 单元格背景颜色
    :param align: 对齐方式
    :param valign: 字体对齐方式
    :return:
    """
    style = workBook.add_format({
        'color': font_color,  # 字体颜色
        'font_size': font_size,  # 字体大小
        'bold': bold,  # 字体加粗
        'fg_color': fg_color,  # 单元格背景颜色
        'align': align,  # 对齐方式
        'valign': valign,  # 字体对齐方式
        'border': 1,

    })
    return style


def statisticDataResult():
    result_data = {}     # 结果数据，里面存储的是所有case下所有最大值的集合
    property_max_data = {}    # 每个文件某列中的最大值
    avg_case_max_data = {}      # 每个case下所有文件某列最大值的平均值
    max_file_num = 0       # 所有case中，里面文件数的最大值

    # 循环结束后，得到所有case下的每个文件的每个列的最大值result_data
    # 循环结束后，得到所有case下每个列的均值avgColValue
    for case, caseValues in sorted(ConfigInfo.baseConfig.items()):
        directory = os.path.dirname(os.getcwd()) + caseValues['directory']
        columns = caseValues['columns']
        result_data[case] = {}
        property_max_data[case] = {}
        avg_case_max_data[case] = {}

        allfiles = glob.glob(os.path.join(directory, '*.csv'))
        count = len(allfiles)
        # 循环结束后，得到该case下所有文件所需列的最大值
        for file in allfiles:
            csv_file_data = pd.read_csv(file)

            # 循环结束后，得到该文件下所需列的最大值
            for col in columns:
                col_data = csv_file_data[col]

                column_data = []
                remove_percentile(col_data, column_data)  # 除去列表中的百分号
                max_column_data = max(column_data)  # 计算每列的最大值

                if col not in result_data[case].keys():
                    result_data[case][col] = []

                # 如果cpu的结果想带%，则使用这一行。注销掉下方result_data[case][col].append(int(max_column_data))
                # result_data[case][col].append(max_column_data)

                if col not in property_max_data[case].keys():
                    property_max_data[case][col] = 0

                result_data[case][col].append(int(max_column_data))
                property_max_data[case][col] += int(max_column_data)

                # 判断是否为CPU%，如果是，求平均值的时候不除以1024*1024
                flag = 0
                if col == 'CPU%':
                    flag = 1
                # 获得每个场景下每列的平均值avg_case_max_data[case][col], 并保留小数点后两位
                avgValue = round(property_max_data[case][col] / count, 2)
                if flag == 1:
                    # avgValue = str(avgValue) + '%'
                    avgValue = avgValue
                else:
                    avgValue = round(avgValue / 1024 / 1024, 2)
                avg_case_max_data[case][col] = avgValue

        # 获得场景下文件数的最大值max_file_num
        if max_file_num < count:
            max_file_num = count

    print(result_data)

    # 设置各种行的样式
    titleStyle = setTitleStyle('black', '18', True, '#2F75B5', 'center', 'vcenter')
    topicStyle = setTitleStyle('black', '16', True, '#9BC2E6', 'left', 'vcenter')
    bodySinStyle = setTitleStyle('black', '14', False, '#D9E1F2', 'left', 'vcenter')
    bodyDouStyle = setTitleStyle('black', '14', False, '#EDEDED', 'left', 'vcenter')
    bodyFailSinStyle = setTitleStyle('red', '14', True, '#D9E1F2', 'left', 'vcenter')
    bodyFailDouStyle = setTitleStyle('red', '14', True, '#EDEDED', 'left', 'vcenter')
    bodySuccSinStyle = setTitleStyle('green', '14', True, '#D9E1F2', 'left', 'vcenter')
    bodySuccDouStyle = setTitleStyle('green', '14', True, '#EDEDED', 'left', 'vcenter')

    # 插入第一行表头
    sheetTitle = "FEED核心场景性能测试报告"
    worksheet.merge_range(0, 0, 0, max_file_num + 3, sheetTitle, titleStyle)

    # 插入第二行数据类型和次数
    sheetColTitle = ['case场景', '类型']
    for i in range(max_file_num):
        sheetColTitle.append(i + 1)
    sheetColTitle.append('avg(G)')
    sheetColTitle.append('通过')
    worksheet.write_row('A2', sheetColTitle, topicStyle)


    # 逐行插入每个类型的数据（如：RSS）
    rows = 3
    caseFlag = 1

    # 设置每个场景的样式
    for case, totalData in result_data.items():
        bodyStyle = bodyDouStyle
        failStyle = bodyFailDouStyle
        succStyle = bodySuccDouStyle
        if caseFlag % 2 == 1:
            bodyStyle = bodySinStyle
            failStyle = bodyFailSinStyle
            succStyle = bodySuccSinStyle
        caseFlag += 1

        # 第一列每次合并单元格的起始位置
        beginPoint = rows - 1
        for col, maxValue in totalData.items():
            dataLength = len(maxValue)

            # rowData:将峰值list和该峰值的均值组成list
            rowData = []
            avgValue = avg_case_max_data[case][col]
            # rowData.append(description)
            rowData.append(col)
            for maxV in maxValue:
                rowData.append(maxV)

            # resultPass：记录是否通过，峰值和峰值的均值是否都小于给定的阈值
            resultPass = ''
            if col in maxCompareData.keys():
                resultPass = compareValue(maxValue, avgValue, maxCompareData[col])

            # 行数和最大行数的差值，不到最大行数就补充应有样式
            diffNum = max_file_num - dataLength
            for i in range(diffNum):
                rowData.append('')

            rowData.append(avgValue)

            # 将峰值list和该峰值的均值组成list（rowData），然后整列写入excel中。
            rowCount = 'B' + str(rows)
            worksheet.write_row(rowCount, rowData, bodyStyle)

            resultStyle = succStyle
            if resultPass == 'Fail':
                resultStyle = failStyle

            # 将判断的结果resultPass追加到最后
            worksheet.write(rows-1, max_file_num+3, resultPass, resultStyle)
            rows += 1

        # 第一列每次合并单元格的结束位置
        endPoint = rows - 2
        description = ConfigInfo.baseConfig[case]['description']
        worksheet.merge_range(beginPoint, 0, endPoint, 0, description, bodyStyle)

    # 设置列的宽度
    worksheet.set_column("A:A", 60)

    endColumn = ord('B') + max_file_num + 1
    endColumnPoint = chr(endColumn)

    worksheet.set_column("B:" + endColumnPoint, 12)

    # 设置行的高度
    for i in range(rows - 1):
        if i == 0:
            worksheet.set_row(i, 45)
        elif i == 1:
            worksheet.set_row(i, 35)
        else:
            worksheet.set_row(i, 25)

    workBook.close()


if __name__ == '__main__':
    statisticDataResult()
