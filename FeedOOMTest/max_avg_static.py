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
work_book = xlsxwriter.Workbook('Report/ResultReport' + time_stamp + '.xlsx')


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


def transpose(m, cases_list):
    tran_avg_max_data = {}
    for key, value in m.items():
        for key2, value2 in value.items():
            if key2 not in tran_avg_max_data.keys():
                tran_avg_max_data[key2] = {}
            tran_avg_max_data[key2][key] = value2

    re_data_map = {}
    for col, col_value in tran_avg_max_data.items():
        avg_list = []
        re_data_map[col] = []
        for item in cases_list:
            if item not in col_value.keys():
                re_data_map[col].append('')
            else:
                re_data_map[col].append(col_value[item])
                avg_list.append(col_value[item])

        avg = round(np.mean(avg_list), 2)
        if col == 'CPU%':
            avg = avg
        elif col == 'VSS':
            avg = round(avg / 1024 / 1024, 2)
        else:
            avg = round(avg / 1024, 2)
        re_data_map[col].append(avg)
    return re_data_map


def statistic_data_result(cases_list):
    result_max_data = {}     # 结果数据，里面存储的是所有case下所有最大值的集合
    result_avg_data = {}     # 结果数据，里面存储的是所有case下所有均值的集合
    property_max_data = {}    # 每个文件某列中的最大值
    property_avg_data = {}    # 每个文件某列中的均值
    avg_case_max_data = {}     # 每个case下所有文件某列最大值的平均值
    avg_case_avg_data = {}  # 每个case下所有文件某列均值的平均值
    max_file_num = 0       # 所有case中，里面文件数的最大值
    cases_description = ''

    # 循环结束后，得到所有case下的每个文件的每个列的最大值result_max_data
    # 循环结束后，得到所有case下每个列的均值avgColValue
    for case, caseValues in sorted(ConfigInfo.baseConfig.items()):
        # directory = os.path.dirname(os.getcwd()) + caseValues['directory']

        if case not in cases_list:
            continue

        cases_description += caseValues['description'] + '\n'
        directory = os.getcwd() + caseValues['directory']

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

                # # 判断是否为CPU%，如果是，求平均值的时候不除以1024*1024
                # flag = 0
                # if col == 'CPU%':
                #     flag = 1
                # 获得每个场景下每列的平均值avg_case_max_data[case][col], 并保留小数点后两位
                avg_max_value = round(property_max_data[case][col] / count, 2)
                avg_avg_value = round(property_avg_data[case][col] / count, 2)
                # if flag == 1:
                #     avg_max_value = avg_max_value
                #     avg_avg_value = avg_avg_value
                # else:
                #     avg_max_value = round(avg_max_value / 1024 / 1024, 2)
                #     avg_avg_value = round(avg_avg_value / 1024 / 1024, 2)
                avg_case_max_data[case][col] = avg_max_value
                avg_case_avg_data[case][col] = avg_avg_value

        # 获得场景下文件数的最大值max_file_num
        if max_file_num < count:
            max_file_num = count

    return max_file_num, result_max_data, avg_case_max_data, result_avg_data, avg_case_avg_data, cases_description


def set_font_style(font_color, font_size, bold, fg_color, align, valign, wrap):
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
        'text_wrap': wrap,    # 自动换行
    })
    return style


def each_line_style():
    """
    设置各种行的样式
    :return:
    """
    title_style = set_font_style('white', '16', True, '#2F75B5', 'center', 'vcenter', 1)
    topic_style = set_font_style('black', '14', True, '#9BC2E6', 'left', 'vcenter', 1)
    body_sin_style = set_font_style('black', '13', False, '#D9E1F2', 'left', 'vcenter', 1)
    body_dou_style = set_font_style('black', '13', False, '#EDEDED', 'left', 'vcenter', 1)
    body_fail_sin_style = set_font_style('red', '13', True, '#D9E1F2', 'left', 'vcenter', 1)
    body_fail_dou_style = set_font_style('red', '13', True, '#EDEDED', 'left', 'vcenter', 1)
    body_succ_sin_style = set_font_style('green', '13', True, '#D9E1F2', 'left', 'vcenter', 1)
    body_succ_dou_style = set_font_style('green', '13', True, '#EDEDED', 'left', 'vcenter', 1)
    return title_style, topic_style, body_sin_style, body_dou_style, body_fail_sin_style, body_fail_dou_style, body_succ_sin_style, body_succ_dou_style


def max_avg_write_to_excel(worksheet, max_file_num, result_data, avg_case_data):
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
        if not totalData:
            continue
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


def write_to_raw(worksheet, content_text1, content_text2, content_text3, style1, style2, raw_num, row_data, row_count):
    worksheet.write(raw_num, 0, content_text1, style1)
    worksheet.merge_range(raw_num, 1, raw_num, 5, content_text2, style1)
    worksheet.write(raw_num, 6, content_text3, style1)
    worksheet.write_row(row_count, row_data, style2)


def get_attr_names(cases_list):

    conf = ConfigInfo.baseConfig
    attrs_set = []
    for item in cases_list:
        if item not in conf.keys():
            continue
        attrs_list = conf[item]['columns']
        attrs_set.extend(attrs_list)
    attrs_set = list(set(attrs_set))
    return attrs_set


def collect_write_to_excel(worksheet, cases_list, re_data_map_avg, re_data_map_max, cases_description):
    """
    将汇总的结果写入excel文件中
    :return:
    """
    title_style = set_font_style('white', '16', True, '#2F75B5', 'center', 'vcenter', 1)
    yellow_style = set_font_style('black', '13', True, '#fafe4b', 'left', 'vcenter', 1)
    title_center_style = set_font_style('white', '12', True, '#2F75B5', 'center', 'vcenter', 1)
    body_left_style = set_font_style('black', '12', True, 'white', 'left', 'vcenter', 1)
    body_left_style2 = set_font_style('black', '12', True, 'white', 'left', 'vcenter', 0)
    body_center_style = set_font_style('black', '12', True, 'white', 'center', 'vcenter', 1)

    max_case_num = 12
    """
    写第一个汇总表
    """
    # 插入第一行
    worksheet.merge_range(0, 0, 0, max_case_num, '性能测试报告', title_style)
    # 插入第二行
    worksheet.write(1, 0, '核心业务', title_center_style)
    worksheet.merge_range(1, 1, 1, 6, 'Feed-Topic', body_left_style)
    worksheet.merge_range(1, 8, 1, 12, 'VSS红线说明', yellow_style)

    # 插入第三行
    worksheet.write(2, 0, '测试机型', title_center_style)
    iphone_type = os.popen('adb shell getprop ro.product.model').read()
    print(iphone_type)
    worksheet.merge_range(2, 1, 2, 6, iphone_type, body_left_style2)
    row_count = 'I3'
    row_data = ['机型', 'ROM', '可用内存', '纯业务', '交叉业务']
    worksheet.write_row(row_count, row_data, title_center_style)

    # 插入第四行
    row_data = ['华为畅享7', '7.0', '3G', '< 2.8G', '< 2.9G']
    write_to_raw(worksheet, '测试内容', '测试说明', '测试结论', title_center_style, body_center_style, 3, row_data, 'I4')

    # 插入第五行
    row_data = ['华为畅享7P', '7.0', '3G', '< 2.8G', '< 2.9G']
    content_text = '整体在20%以下，且退出后CPU能收敛至0，若均值超过20%、峰值超过40%、退出静置后未收敛均视为超标'
    write_to_raw(worksheet, 'CPU', content_text, '', body_left_style, body_center_style, 4, row_data, 'I5')

    # 插入第六行
    row_data = ['华为荣耀6A', '7.0', '3G', '< 2.8G', '< 2.9G']
    content_text = '纯业务/交叉业务场景下，VSS消耗低于2.8G，符合预期'
    write_to_raw(worksheet, '虚拟内存VSS', content_text, '', body_left_style, body_center_style, 5, row_data, 'I6')

    # 插入第七行
    row_data = ['三星C5000', '7.0', '3G', '< 2.8G', '< 2.9G']
    content_text = '纯业务/交叉业务场景下，RSS数据稳定波动、且静置后正常回收，若出现持续增长、不进行回收均视为超标'
    write_to_raw(worksheet, '常驻内存RSS', content_text, '', body_left_style,  body_center_style, 6, row_data, 'I7')

    # 插入第八行
    row_data = ['华为Mate20', '7.0/8.0', '3G', '< 3.7G', '< 3.8G']
    content_text = '纯业务/交叉业务场景下，VSS数据稳定波动、且静置后正常回收，若出现持续增长、不进行回收均视为超标'
    write_to_raw(worksheet, '物理内存PSS', content_text, '', body_left_style,  body_center_style, 7, row_data, 'I8')

    # """
    # 写第二个CPU表
    # """
    attrs_set = get_attr_names(cases_list)
    flag_excel = 0
    for item in sorted(attrs_set):
        content_text = '报告说明：需要提供汇总的数据及图形报表，详细测试数据以附表形式贴在表2、表3中。'
        worksheet.merge_range(10, 0, 10, 7 + len(cases_list), content_text, yellow_style)
        worksheet.merge_range(11, 0, 11, 7 + len(cases_list), '测试数据', title_style)
        worksheet.merge_range(12 + 8 * flag_excel, 0, 12 + 8 * flag_excel, 7 + len(cases_list), str(flag_excel + 1)+'. ' + item, yellow_style)

        # 插入表头
        worksheet.merge_range(13 + 8 * flag_excel, 0, 13 + 8 * flag_excel, 3, '测试场景', title_center_style)
        sheet_col_title = []
        sheet_col_title.append(item)
        sheet_col_title.append('版本对比')
        for i in range(len(cases_list)):
            sheet_col_title.append('场景' + str(i + 1))
        if item == 'CPU%':
            type = '均值（%）'
        elif item == 'VSS':
            type = '均值（GB）'
        else:
            type = '均值（MB）'
        sheet_col_title.append(type)
        sheet_col_title.append('GAP(%)')
        chart_index = 'E' + str(14 + 8 * flag_excel)
        worksheet.write_row(chart_index, sheet_col_title, title_center_style)

        # 插入里面的数据内容
        worksheet.merge_range(14 + 8 * flag_excel, 0, 17 + 8 * flag_excel, 0, '纯业务', body_center_style)
        worksheet.merge_range(14 + 8 * flag_excel, 1, 17 + 8 * flag_excel, 3, cases_description, body_left_style)

        worksheet.merge_range(14 + 8 * flag_excel, 4, 15 + 8 * flag_excel, 4, '峰值', body_center_style)
        worksheet.merge_range(16 + 8 * flag_excel, 4, 17 + 8 * flag_excel, 4, '均值', body_center_style)
        chart_index = 'F' + str(15 + 8 * flag_excel)
        column_data = ['测试版本', '线上版本', '测试版本', '线上版本']
        worksheet.write_column(chart_index, column_data, body_center_style)
        chart_index = 'G' + str(15 + 8 * flag_excel)

        re_data_map_max[item].append('')
        worksheet.write_row(chart_index, re_data_map_max[item], body_center_style)
        chart_index = 'G' + str(16 + 8 * flag_excel)
        bb = ['' for _ in range(len(re_data_map_max[item]))]
        worksheet.write_row(chart_index, bb, body_center_style)

        re_data_map_avg[item].append('')
        chart_index = 'G' + str(17 + 8 * flag_excel)
        worksheet.write_row(chart_index, re_data_map_avg[item], body_center_style)
        chart_index = 'G' + str(18 + 8 * flag_excel)
        worksheet.write_row(chart_index, bb, body_center_style)
        flag_excel += 1

    max_row_number = 18 + 8 * (flag_excel - 1)
    # 设置列的宽度
    worksheet.set_column("A:A", 14)
    worksheet.set_column("B:E", 26)
    worksheet.set_column("E:V", 11)

    # 设置行的高度
    for i in range(max_row_number):
        if i == 0:
            worksheet.set_row(i, 45)
        elif i < 10:
            worksheet.set_row(i, 20)
        else:
            worksheet.set_row(i, 23)


def max_avg_report(cases_list):
    worksheet_collect = work_book.add_worksheet('性能测试报告')
    worksheet_max = work_book.add_worksheet('峰值')
    worksheet_avg = work_book.add_worksheet('均值')

    get_attr_names(cases_list)
    max_file_num, result_max_data, avg_case_max_data, result_avg_data, avg_case_avg_data, cases_description = statistic_data_result(
        cases_list)

    re_data_map_max = transpose(avg_case_max_data, cases_list)
    re_data_map_avg = transpose(avg_case_avg_data, cases_list)

    collect_write_to_excel(worksheet_collect, cases_list, re_data_map_avg, re_data_map_max, cases_description)
    max_avg_write_to_excel(worksheet_max, max_file_num, result_max_data, avg_case_max_data)
    max_avg_write_to_excel(worksheet_avg, max_file_num, result_avg_data, avg_case_avg_data)
    work_book.close()


if __name__ == '__main__':
    worksheet_collect = work_book.add_worksheet('性能测试报告')
    worksheet_max = work_book.add_worksheet('峰值')
    worksheet_avg = work_book.add_worksheet('均值')

    cases_list = ['case1', 'case2', 'case3', 'case4', 'case5']
    get_attr_names(cases_list)
    max_file_num, result_max_data, avg_case_max_data, result_avg_data, avg_case_avg_data, cases_description = statistic_data_result(cases_list)

    re_data_map_max = transpose(avg_case_max_data, cases_list)
    re_data_map_avg = transpose(avg_case_avg_data, cases_list)

    collect_write_to_excel(worksheet_collect, cases_list, re_data_map_avg, re_data_map_max, cases_description)
    max_avg_write_to_excel(worksheet_max, max_file_num, result_max_data, avg_case_max_data)
    max_avg_write_to_excel(worksheet_avg, max_file_num, result_avg_data, avg_case_avg_data)
    work_book.close()


