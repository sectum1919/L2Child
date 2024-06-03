# -*- encoding: utf-8 -*-
'''
Filename         :analyze_common_utils.py
Description      :提取标注信息、绘制热力图的共用函数和定义
Time             :2024/04/26 16:57:46
Author           :chenchen
'''


import json
import numpy as np
import copy
# 声母、韵母、声调横纵轴的所有可能取值
all_keys = {
    'initial': [
        'b',
        'p',
        'd',
        't',
        'g',
        'k',  # 6
        'f',
        's',
        'sh',
        'x',
        'h',  # 5
        'z',
        'c',
        'zh',
        'ch',
        'j',
        'q',  # 6 
        'm',
        'n',
        'l',
        'r',  # 4
        '*',
    ],
    'consonant': [
        'a',
        'o',
        'e',
        'er',
        'ai',
        'ei',
        'ao',
        'ou',
        'an',
        'en',
        'ang',
        'eng',  # 12
        'i',
        'ia',
        'ie',
        'iao',
        'iu',
        'ian',
        'in',
        'iang',
        'ing',  # 9
        'u',
        'ua',
        'uo',
        'uai',
        'ui',
        'uan',
        'un',
        'uang',
        'ong',  # 9
        'v',
        've',
        'van',
        'vn',
        'iong',  # 5
        '*'
    ],
    '结构': [
        'a',
        'o',
        'e',
        'er',
        'i',
        'u',
        'v', # 7 单韵母
        'ai',
        'ei',
        'ao',
        'ou',
        'ia',
        'ie',
        'ua',
        'uo',
        've',
        'iao',
        'iu',
        'uai',
        'ui', # 13 复韵母
        'an',
        'ian',
        'uan',
        'van',
        'en',
        'in',
        'un',
        'vn',
        'ang',
        'iang',
        'uang',
        'eng',  
        'ing',  
        'ong',  
        'iong',  # 15 鼻韵母 
        '*'
    ],
    'tone': ['1', '2', '3', '4', '5', '*'],
}
# 分组位置
split_pos = {
    'initial': [6, 11, 17],
    'consonant': [12, 21, 30],
    '结构': [7, 20],
    'tone': [],
}
# 忽略阈值
threshold = {
    # 'initial': 0.5,
    # 'consonant': 1.0,
    # '结构': 1.0,
    # 'tone': 1e-6,
    'initial': 1e-6,
    'consonant': 1e-6,
    '结构': 1e-6,
    'tone': 1e-6,
}
fig_size = {
    'initial': (16, 12),
    'consonant': (32, 25),
    '结构': (32, 25),
    'tone': (4, 5),
}
font_size = {
    'initial': 4,
    'consonant': 4,
    '结构': 4,
    'tone': 4,
}
num_format = {
    'initial': '.2f',
    'consonant': '.2f',
    '结构':'.2f',
    'tone':'.5f',
}
dpis = {
    'initial': 1000,
    'consonant': 1000,
    '结构': 1000,
    'tone': 500,
}

def draw_heatmap(probs, threshold, split_pos, x_ticks, y_ticks, font_size, num_format, discard_diag, size_t, dpi, save_path, format_save):
    # 画图是先横行后竖列，故按照先y后x的方法取数值
    # 画图从上到下，从左到右
    heatmap = np.zeros((len(y_ticks), len(x_ticks)))
    mask = np.zeros((len(y_ticks), len(x_ticks)))
    for i, y in enumerate(y_ticks):
        for j, x in enumerate(x_ticks):
            if discard_diag and x == y:
                mask[i][j] = True
            else:
                mask[i][j] = False
            heatmap[i][j] = probs[x][y] * 100
            # 忽略数值较小的
            if heatmap[i][j] < threshold:
                mask[i][j] = True
    import matplotlib.pyplot as plt
    import seaborn as sns  #导入包
    plt.cla()
    plt.clf()
    sns.set_context({"figure.figsize": size_t})
    plt.rcParams['font.size'] = font_size
    p = sns.heatmap(
        heatmap,
        cmap="BuPu",
        cbar=False,
        mask=mask,
        square=True,
        annot=True,
        fmt=num_format,
        linecolor='black',
        linewidths=0.5,
        # vmin=0,
        # vmax=100,
        xticklabels=x_ticks,
        yticklabels=y_ticks,
    )
    if len(split_pos) > 0:
        p.hlines([len(y_ticks) - pos for pos in split_pos], *p.get_xlim())
        p.vlines(split_pos, *p.get_ylim())
    # 画热力图,annot=True 代表 在图上显示 对应的值， fmt 属性 代表输出值的格式，cbar=False, 不显示 热力棒
    plt.yticks(rotation=0)
    plt.xticks(rotation=0)

    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=dpi, format=format_save)
                