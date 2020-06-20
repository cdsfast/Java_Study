# coding=utf-8
__author__ = 'lixuefang'

from max_avg_static import max_avg_report
from ConfigInfo import baseConfig
from PublicUtils.public_functions import dirIsExist
import os


# 判断生成报告的文件夹Report是否存在，如果存在删除，否则创建
dirIsExist('Report')


def scene_execute(scene, case):
    """

    :return:
    """

    # 每个场景生成性能数据的文件夹路径path_case1
    path_case = os.getcwd() + baseConfig[scene]['directory'] + '/'
    # 判断这个文件夹是否存在，如果已经存在则删除，否则重新创建
    dirIsExist(path_case)
    command_string = 'python ' + os.getcwd() + '/TestCases/' + case + '.py'
    for i in range(10):
        # 异步执行收集性能数据的脚本
        os.system("nohup python get_cpu_memory_v3.py -c " + path_case + " >> nohup.out &")
        # 执行自动化case脚本
        os.system(command_string)


if __name__ == '__main__':
    case_lists = ['case1', 'case2', 'case3']
    scene_execute('case1', 'FeedPerformanceCase')
    scene_execute('case2', 'FeedPerformanceCase2')
    scene_execute('case3', 'FeedPerformanceCase3')

    max_avg_report(case_lists)
    # diffValueStatistic.caculateDiffData()
