# coding=utf-8
__author__ = 'lixuefang'

import ConfigInfo
from ConfigInfo import maxCompareData
import pandas as pd
import glob
import os
import time
import xlsxwriter
import numpy as np


# 创建要生成的报告result.xlsx
time_stamp = time.strftime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
work_book = xlsxwriter.Workbook('../Report/ResultReport' + time_stamp + '.xlsx')


def compare_result(max_value_list, avg_max_value, standard_value):
    """
    判断峰值的list和均值是否否小于给定的阈值，如果全都小于，则Pass，否则Fail
    :param max_value_list:  求每个属性的峰值后，组成的list值
    :param avg_max_value: 峰值的均值
    :param standard_value: 给定的阈值
    :return:
    """
    flag = 'Pass'
    for item in max_value_list:
        if item >= standard_value * 1024 * 1024:
            flag = 'Fail'
            break
    if avg_max_value >= standard_value:
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


def statistic_data_result():
    result_max_data = {}     # 结果数据，里面存储的是所有case下所有最大值的集合
    result_avg_data = {}     # 结果数据，里面存储的是所有case下所有均值的集合
    property_max_data = {}    # 每个文件某列中的最大值
    property_avg_data = {}    # 每个文件某列中的均值
    avg_case_max_data = {}     # 每个case下所有文件某列最大值的平均值
    avg_case_avg_data = {}  # 每个case下所有文件某列均值的平均值
    max_file_num = 0       # 所有case中，里面文件数的最大值

    # 循环结束后，得到所有case下的每个文件的每个列的最大值result_max_data
    # 循环结束后，得到所有case下每个列的均值avgColValue
    for case, caseValues in sorted(ConfigInfo.baseConfig.items()):
        directory = os.path.dirname(os.getcwd()) + caseValues['directory']
        columns = caseValues['columns']
        result_max_data[case] = {}
        result_avg_data[case] = {}
        property_max_data[case] = {}
        property_avg_data[case] = {}
        avg_case_max_data[case] = {}
        avg_case_avg_data[case] = {}

        allfiles = glob.glob(os.path.join(directory, '*.csv'))
        count = len(allfiles)

        # 循环结束后，得到该case下所有文件所需列的最大值
        for file in allfiles:
            csv_file_data = pd.read_csv(file)

            # 循环结束后，得到该文件下所需列的最大值
            for col in columns:
                col_data = csv_file_data[col]

                column_data = []
                remove_percentile(col_data, column_data)  # 去除列表中的百分号
                max_column_data = max(column_data)  # 计算每列的最大值
                avg_column_data = np.mean(column_data)  # 计算每列的均值

                if col not in result_max_data[case].keys():
                    result_max_data[case][col] = []
                result_max_data[case][col].append(int(max_column_data))

                if col not in result_avg_data[case].keys():
                    result_avg_data[case][col] = []
                result_avg_data[case][col].append(int(avg_column_data))

                if col not in property_max_data[case].keys():
                    property_max_data[case][col] = 0
                property_max_data[case][col] += int(max_column_data)

                if col not in property_avg_data[case].keys():
                    property_avg_data[case][col] = 0
                property_avg_data[case][col] += int(avg_column_data)

                # 判断是否为CPU%，如果是，求平均值的时候不除以1024*1024
                flag = 0
                if col == 'CPU%':
                    flag = 1
                # 获得每个场景下每列的平均值avg_case_max_data[case][col], 并保留小数点后两位
                avg_max_value = round(property_max_data[case][col] / count, 2)
                avg_avg_value = round(property_avg_data[case][col] / count, 2)
                if flag == 1:
                    avg_max_value = avg_max_value
                    avg_avg_value = avg_avg_value
                else:
                    avg_max_value = round(avg_max_value / 1024 / 1024, 2)
                    avg_avg_value = round(avg_avg_value / 1024 / 1024, 2)
                avg_case_max_data[case][col] = avg_max_value
                avg_case_avg_data[case][col] = avg_avg_value

        # 获得场景下文件数的最大值max_file_num
        if max_file_num < count:
            max_file_num = count

    return max_file_num, result_max_data, avg_case_max_data, result_avg_data, avg_case_avg_data


def set_font_style(font_color, font_size, bold, fg_color, align, valign):
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

    style = work_book.add_format({
        'color': font_color,  # 字体颜色
        'font_size': font_size,  # 字体大小
        'bold': bold,  # 字体加粗
        'fg_color': fg_color,  # 单元格背景颜色
        'align': align,  # 对齐方式
        'valign': valign,  # 字体对齐方式
        'border': 1,

    })
    return style


def each_line_style():
    """
    设置各种行的样式
    :return:
    """
    title_style = set_font_style('black', '18', True, '#2F75B5', 'center', 'vcenter')
    topic_style = set_font_style('black', '16', True, '#9BC2E6', 'left', 'vcenter')
    body_sin_style = set_font_style('black', '14', False, '#D9E1F2', 'left', 'vcenter')
    body_dou_style = set_font_style('black', '14', False, '#EDEDED', 'left', 'vcenter')
    body_fail_sin_style = set_font_style('red', '14', True, '#D9E1F2', 'left', 'vcenter')
    body_fail_dou_style = set_font_style('red', '14', True, '#EDEDED', 'left', 'vcenter')
    body_succ_sin_style = set_font_style('green', '14', True, '#D9E1F2', 'left', 'vcenter')
    body_succ_dou_style = set_font_style('green', '14', True, '#EDEDED', 'left', 'vcenter')
    return title_style, topic_style, body_sin_style, body_dou_style, body_fail_sin_style, body_fail_dou_style, body_succ_sin_style, body_succ_dou_style


def write_to_excel(worksheet, max_file_num, result_data, avg_case_data):
    """
    :return:
    """
    title_style, topic_style, body_sin_style, body_dou_style, body_fail_sin_style, body_fail_dou_style, body_succ_sin_style, body_succ_dou_style = each_line_style()

    # 插入第一行表头
    sheet_title = "FEED核心场景性能测试报告"
    worksheet.merge_range(0, 0, 0, max_file_num + 3, sheet_title, title_style)

    # 插入第二行数据类型和次数
    sheet_col_title = ['case场景', '类型']
    for i in range(max_file_num):
        sheet_col_title.append(i + 1)
    sheet_col_title.append('avg(G)')
    sheet_col_title.append('通过')
    worksheet.write_row('A2', sheet_col_title, topic_style)

    # 逐行插入每个类型的数据（如：RSS）
    rows = 3
    case_flag = 1

    # 设置每个场景的样式
    for case, totalData in result_data.items():
        body_style = body_dou_style
        fail_style = body_fail_dou_style
        succ_style = body_succ_dou_style
        if case_flag % 2 == 1:
            body_style = body_sin_style
            fail_style = body_fail_sin_style
            succ_style = body_succ_sin_style
        case_flag += 1

        # 第一列每次合并单元格的起始位置
        begin_point = rows - 1
        for col, maxValue in totalData.items():
            data_length = len(maxValue)

            # row_data:将峰值list和该峰值的均值组成list
            row_data = []
            avg_max_value = avg_case_data[case][col]
            # row_data.append(description)
            row_data.append(col)
            for maxV in maxValue:
                row_data.append(maxV)

            # result_pass：记录是否通过，峰值和峰值的均值是否都小于给定的阈值
            result_pass = ''
            if col in maxCompareData.keys():
                result_pass = compare_result(maxValue, avg_max_value, maxCompareData[col])

            # 行数和最大行数的差值，不到最大行数就补充应有样式
            diff_num = max_file_num - data_length
            for i in range(diff_num):
                row_data.append('')

            row_data.append(avg_max_value)

            # 将峰值list和该峰值的均值组成list（row_data），然后整列写入excel中。
            row_count = 'B' + str(rows)
            worksheet.write_row(row_count, row_data, body_style)

            result_style = succ_style
            if result_pass == 'Fail':
                result_style = fail_style

            # 将判断的结果result_pass追加到最后
            worksheet.write(rows - 1, max_file_num + 3, result_pass, result_style)
            rows += 1

        # 第一列每次合并单元格的结束位置
        end_point = rows - 2
        description = ConfigInfo.baseConfig[case]['description']
        worksheet.merge_range(begin_point, 0, end_point, 0, description, body_style)

    # 设置列的宽度
    worksheet.set_column("A:A", 60)

    end_column = ord('B') + max_file_num + 1
    end_column_point = chr(end_column)

    worksheet.set_column("B:" + end_column_point, 12)

    # 设置行的高度
    for i in range(rows - 1):
        if i == 0:
            worksheet.set_row(i, 45)
        elif i == 1:
            worksheet.set_row(i, 35)
        else:
            worksheet.set_row(i, 25)


def max_avg_report():
    worksheet_max = work_book.add_worksheet('峰值')
    worksheet_avg = work_book.add_worksheet('均值')

    max_file_num, result_max_data, avg_case_max_data, result_avg_data, avg_case_avg_data = statistic_data_result()
    write_to_excel(worksheet_max, max_file_num, result_max_data, avg_case_max_data)
    write_to_excel(worksheet_avg, max_file_num, result_avg_data, avg_case_avg_data)
    work_book.close()


if __name__ == '__main__':
    worksheet_max = work_book.add_worksheet('峰值')
    worksheet_avg = work_book.add_worksheet('均值')

    max_file_num, result_max_data, avg_case_max_data, result_avg_data, avg_case_avg_data = statistic_data_result()
    write_to_excel(worksheet_max, max_file_num, result_max_data, avg_case_max_data)
    write_to_excel(worksheet_avg, max_file_num, result_avg_data, avg_case_avg_data)
    work_book.close()


