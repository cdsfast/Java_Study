# coding=utf-8
__author__ = 'lixuefang'

import os

path = os.getcwd()

baseConfig = {
    'case1': {
        'directory': '/Data/case1_refresh',
        'columns': ['CPU%', 'VSS', 'RSS', 'PSS'],
        'time_columns': ['CPU%',  'VSS', 'RSS', 'PSS'],
        'time_file': 'time_case1.txt',
        'description': 'Case: 冷启动->静置30s->反复刷新10次->直到数据完全展现'
    },

    'case2': {
        'directory': '/Data/case2_refresh',
        'columns': ['CPU%', 'VSS', 'RSS', 'PSS'],
        'time_columns': ['CPU%', 'RSS', 'VSS'],
        'time_file': 'time_case2.txt',
        'description': 'Case: 冷启动->静置30s->反复进入同一落地页10次->直到相关推荐展现，评论展现一屏->返回列表'
    },
    'case3': {
        'directory': '/Data/case3_refresh',
        'columns': ['CPU%', 'RSS', 'VSS', 'PSS'],
        'time_columns': ['CPU%', 'RSS'],
        'time_file': 'time_case3.txt',
        'description': 'Case: 冷启动->静置30s->反复进入10篇不同的图文落地页，直到相关推荐展现，评论展现一屏幕>返回列表'
    },
    'case4': {
        'directory': '/Data/case4_refresh',
        'columns': ['CPU%', 'RSS', 'VSS', 'PSS'],
        'time_columns': ['CPU%', 'RSS'],
        'time_file': 'time_case4.txt',
        'description': 'Case: 冷启动->静置30s->反复进入同一篇图集落地页10次，至相关推荐展现->返回列表'
    },
    'case5': {
        'directory': '/Data/case5_refresh',
        'columns': ['CPU%', 'RSS', 'VSS', 'PSS'],
        'time_columns': ['CPU%', 'RSS'],
        'time_file': 'time_case5.txt',
        'description': 'Case: 冷启动->静置30s-> 反复进入10篇不同的图集落地页，至相关推荐展现->返回列表'
    },

}

# 设置maxValueStatistics（峰值）需要判断的属性以及每个属性的阈值
maxCompareData = {
    'VSS': 2800000,
    'RSS': 500000,
    'PSS': 560208,
    'CPU%': 80,

}

# 设置diffValueStatistics（稳定性）需要判断的属性以及每个属性的阈值
diffCompareData = {
    'CPU%': {
        'avg': 80,
        'diff': 5,
    },
    'RSS': {
        'avg': 600000,
        'diff': 10000,
    }
}
