# coding=utf-8
__author__ = 'lixuefang'
"""
之前单计算和生成差值的脚本，目前已不用。
"""
import os
import glob
import time
import pandas as pd
import xlsxwriter
from ConfigInfo import baseConfig, diffCompareData


time_stamp = time.strftime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
# 创建要生成的报告result.xlsx
workBook = xlsxwriter.Workbook('../Report/DiffResultReport' + time_stamp + '.xlsx')
worksheet = workBook.add_worksheet()


# 读取时间timeA 和 timeB的文件，存储到list中
def readTimeFile(timeFile):
    with open(timeFile, 'r') as f:
        data = f.readlines()
        data = ''.join(data).strip('\n').splitlines()
        return data


# 获取时间timeD 在timeList中的位置
def caculateIndex(timeList, timeD):
    lTimeList = len(timeList)
    index = lTimeList - 1
    for i in range(lTimeList):
        if timeD <= timeList[i]:
            index = i
            break
    # 如果之前有五条数据，则indexBegin为前面第5条的位置，否则为0
    if index > 4:
        indexBegin = index - 4
    else:
        indexBegin = 0
    indexEnd = index
    return indexBegin, indexEnd


# 计算dataList的平均值
def avgVaule(dataList):
    sumData = 0
    flag = 0
    for value in dataList:
        if '%' in str(value):
            flag = 1
            value = value.strip('%')
        sumData += float(value)
    avgData = round(sumData / len(dataList), 2)
    # if flag == 1:
    #     avgData = str(avgData) + '%'
    return avgData


# 计算两个值之间的差值
def diffData(dataA, dataB):
    if '%' in str(dataA):
        dataA = dataA.strip('%')
        dataB = dataB.strip('%')
        diffData = round(float(dataB) - float(dataA), 2)
        # diffData = str(diffData) + '%'
    else:
        diffData = round(float(dataB) - float(dataA), 2)
    return diffData


# 创建要生成报告的样式
def setTitleStyle(font_color, font_size, bold, fg_color, align, valign):
    style = workBook.add_format({
        'color': font_color,     # 字体颜色
        'font_size': font_size,       # 字体大小
        'bold': bold,            # 字体加粗
        'fg_color': fg_color,   # 单元格背景颜色
        'align': align,     # 对齐方式
        'valign': valign,   # 字体对齐方式
        'border': 1,

    })
    return style


def compareValue(listValue, avgValue, standardValue):
    flag = 'Pass'
    for item in listValue:
        if item >= standardValue:
            flag = 'Fail'
            break
    if avgValue >= standardValue:
        flag = 'Fail'
    return flag


def caculateDiffData():
    '''结果数据，里面存储的是所有case下所有最大值的集合。这个数据结构是字典中套字典再套字典，value是list
    {
    case1:
          'RSS':{
                  'avgA': [],
                  'avgB': [],
                  'diffAB': []
                  },
          'CPU%':{
                  'avgA': [],
                  'avgB': [],
                  'diffAB': []
                  }
    case2:
          ...
    }'''

    # resultData：存储关键步骤A和B前5条数据的均值，并求avgB减avgA的差值
    resultData = {}

    # 所有case中，里面文件数的最大值
    maxFileNum = 0

    for case, caseVaules in sorted(baseConfig.items()):
        print(case)
        resultData[case] = {}

        # step1： 获取性能数据文件夹路径
        directory = os.path.dirname(os.getcwd()) + caseVaules['directory']
        timeColumns = caseVaules['time_columns']
        # 获取时间A和B, 存储到list中
        timeList = readTimeFile(directory + '/' + caseVaules['time_file'])

        # step2： 获取所有csv的性能数据文件
        allfiles = glob.glob(os.path.join(directory, '*.csv'))
        fileIndex = 0
        count = len(allfiles)

        # step3： 根据指定列读取每个文件的性能数据列
        for file in allfiles:
            csvFileData = pd.read_csv(file)

            # step3-1： 拿到每个文件的时间戳列
            columnTimeData = csvFileData['TIME']

            # step3-2: 获取timeA 和 timeB
            timeAB = timeList[fileIndex].split(",")
            timeA = timeAB[0]
            timeB = timeAB[1]

            # step3-3：查找timeA 和timeB在文件中的位置
            beginA, endA = caculateIndex(columnTimeData, timeA)
            beginB, endB = caculateIndex(columnTimeData, timeB)

            # step3-4：循环指定的性能列获取begin和end（5条）的数据
            for col in timeColumns:
                dataA = csvFileData[col][beginA: endA+1]
                dataB = csvFileData[col][beginB: endB+1]
                avgA = avgVaule(dataA)
                avgB = avgVaule(dataB)
                diffAB = diffData(avgA, avgB)

                if col not in resultData[case].keys():
                    resultData[case][col] = {}
                    resultData[case][col]['avgA'] = []
                    resultData[case][col]['avgB'] = []
                    resultData[case][col]['diffAB'] = []
                resultData[case][col]['avgA'].append(avgA)
                resultData[case][col]['avgB'].append(avgB)
                resultData[case][col]['diffAB'].append(diffAB)

            fileIndex += 1

        # 获得场景下文件数的最大值maxFileNum
        if maxFileNum < count:
            maxFileNum = count

    # 调用setTitleStyle函数设置不同的样式
    titleStyle = setTitleStyle('black', '18', True, '#2F75B5', 'center', 'vcenter')
    topicStyle = setTitleStyle('black', '16', True, '#9BC2E6', 'left', 'vcenter')
    bodySinStyle = setTitleStyle('black', '14', False, '#D9E1F2', 'left', 'vcenter')
    bodyDouStyle = setTitleStyle('black', '14', False, '#EDEDED', 'left', 'vcenter')
    bodyFailSinStyle = setTitleStyle('red', '14', True, '#D9E1F2', 'left', 'vcenter')
    bodyFailDouStyle = setTitleStyle('red', '14', True, '#EDEDED', 'left', 'vcenter')
    bodySuccSinStyle = setTitleStyle('green', '14', True, '#D9E1F2', 'left', 'vcenter')
    bodySuccDouStyle = setTitleStyle('green', '14', True, '#EDEDED', 'left', 'vcenter')

    # 第一行插入表头
    sheetTitle = "FEED核心场景性能测试报告"
    worksheet.merge_range(0, 0, 0, maxFileNum + 4, sheetTitle, titleStyle)
    # 第二行插入数据类型和次数
    worksheet.write(1, 0, '步骤', topicStyle)
    worksheet.merge_range(1, 1, 1, 2, '类型', topicStyle)
    for i in range(maxFileNum):
        worksheet.write(1, i + 3, i+1, topicStyle)
    worksheet.write(1, maxFileNum+3, 'avg', topicStyle)
    worksheet.write(1, maxFileNum + 4, '通过', topicStyle)

    # 逐行插入每个类型的数据（如：RSS）
    rows = 2
    caseFlag = 1
    for case, dataResult in resultData.items():
        bodyStyle = bodyDouStyle
        failStyle = bodyFailDouStyle
        succStyle = bodySuccDouStyle
        if caseFlag % 2 == 1:
            bodyStyle = bodySinStyle
            failStyle = bodyFailSinStyle
            succStyle = bodySuccSinStyle
        caseFlag += 1

        # 获取这个case下总共的列数
        rowsLen = len(dataResult.keys())
        # 写入第一列case的描述
        worksheet.merge_range(rows, 0, rows + 3 * rowsLen - 1, 0, baseConfig[case]['description'], bodyStyle)

        beginIndex = rows

        for typeColumn, typeData in dataResult.items():
            endIndex = beginIndex + 2
            # 写入第二列数据类型
            worksheet.merge_range(beginIndex, 1, endIndex, 1, typeColumn, bodyStyle)

            # 写入第三列avgA等信息
            worksheet.write(beginIndex, 2, 'avgA', bodyStyle)
            worksheet.write(beginIndex+1, 2, 'avgB', bodyStyle)
            worksheet.write(beginIndex+2, 2, 'diffBA', bodyStyle)

            # 写入之后每一次的值
            rowCountA = 'D' + str(beginIndex+1)
            rowCountB = 'D' + str(beginIndex+2)
            rowCountBA = 'D' + str(beginIndex + 3)

            listAvgA = typeData['avgA']
            listAvgB = typeData['avgB']
            listAvgAB = typeData['diffAB']

            avgA_avg = avgVaule(listAvgA)
            avgB_avg = avgVaule(listAvgB)
            avgAB_avg = avgVaule(listAvgAB)

            if typeColumn in diffCompareData.keys():
                # 判断数据是否通过
                resultAvgA = compareValue(listAvgA, avgA_avg, diffCompareData[typeColumn]['avg'])
                resultAvgB = compareValue(listAvgB, avgB_avg, diffCompareData[typeColumn]['avg'])
                resultAvgAB = compareValue(listAvgAB, avgAB_avg, diffCompareData[typeColumn]['diff'])

            dataLen = len(typeData['avgA'])

            # 如果该场景的文件数小于最大场景的文件数，则其他空白的地方补充本行所用的样式
            diffNum = maxFileNum - dataLen
            for i in range(diffNum):
                listAvgA.append('')
                listAvgB.append('')
                listAvgAB.append('')

            # 分别将listAvgA、listAvgB、listAvgAB的平均值avgA_avg、avgB_avg、avgAB_avg追加到list中
            listAvgA.append(avgA_avg)
            listAvgB.append(avgB_avg)
            listAvgAB.append(avgAB_avg)

            # 分别将最终得到的listAvgA、listAvgB、listAvgAB整个list加入到excel中
            worksheet.write_row(rowCountA, listAvgA, bodyStyle)
            worksheet.write_row(rowCountB, listAvgB, bodyStyle)
            worksheet.write_row(rowCountBA, listAvgAB, bodyStyle)

            # 分别判断resultStyleA、resultStyleB、resultStyleAB的样式
            resultStyleA = succStyle
            if resultAvgA == 'Fail':
                resultStyleA = failStyle

            resultStyleB = succStyle
            if resultAvgB == 'Fail':
                resultStyleB = failStyle

            resultStyleAB = succStyle
            if resultAvgAB == 'Fail':
                resultStyleAB = failStyle

            # 将result的结果写入最后一列
            worksheet.write(beginIndex, maxFileNum + 4, resultAvgA, resultStyleA)
            worksheet.write(beginIndex + 1, maxFileNum + 4, resultAvgB, resultStyleB)
            # worksheet.write(beginIndex, maxFileNum + 4, '', resultStyleAB)
            # worksheet.write(beginIndex + 1, maxFileNum + 4, '', resultStyleAB)
            worksheet.write(beginIndex + 2, maxFileNum + 4, resultAvgAB, resultStyleAB)

            beginIndex = endIndex + 1
        rows += rowsLen * 3

    remarks = '备注：avgA为关键步骤A前5条数据的平均值， avgB为关键步骤B前5条数据的平均值， diffBA为avgB-avgA的差值'
    worksheet.merge_range(beginIndex, 0, beginIndex + 1, maxFileNum + 4, remarks, bodyStyle)

    # 设置列的宽度
    worksheet.set_column("A:A", 60)

    endColumn = ord('B') + maxFileNum + 2
    endColumnPoint = chr(endColumn)

    worksheet.set_column("B:" + endColumnPoint, 12)

    # 设置每行的高度
    for i in range(rows):
        if i == 0:
            worksheet.set_row(i, 45)
        elif i == 1:
            worksheet.set_row(i, 35)
        else:
            worksheet.set_row(i, 25)

    workBook.close()


if __name__ == '__main__':
    caculateDiffData()
