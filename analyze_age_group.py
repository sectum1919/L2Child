# -*- encoding: utf-8 -*-
'''
Filename         :analyze_age_group.py
Description      :划分年龄和性别，按照投票结果/汇总结果绘制热力图
Time             :2024/04/26 16:58:24
Author           :chenchen
'''


import json
import numpy as np
import copy

from analyze_common_utils import *

def count_vote(age_range, sex=None):
    # 采用投票后结果统计错误
    # 初始化每个取值的计数器
    all_counts = {
        'initial':{},
        'consonant':{},
        'tone':{},
    }
    for key in ['initial', 'consonant', 'tone']:
        for target in all_keys[key]:
            all_counts[key][target] = {}
            for spoken in all_keys[key]:
                all_counts[key][target][spoken] = 0
        
    subject_info = json.load(open('data/subject_id2info.json', encoding='gbk'))
    all_char_info = json.load(open('data/all_char_vote.json'))
    
    # 根据所有结果计数
    for subjectid, all_chars in all_char_info.items():
        age = subject_info[subjectid]['age_month']
        # 性别过滤
        if sex is not None:
            if subject_info[subjectid]['sex'] != sex:
                continue
        # 忽略月龄在范围以外的
        if age <= age_range[1] and age_range[0] <= age:
            for char in all_chars:
                for key in ['initial', 'consonant', 'tone']:
                    target = char['target'][key]
                    spoken = char['spoken'][key]
                    if target == '-':
                        continue
                    if target not in all_keys[key]:
                        # print(target)
                        target = '*'
                    if spoken not in all_keys[key]:
                        # print(spoken)
                        spoken = '*'
                    all_counts[key][target][spoken] += 1
    return all_counts
    

def count_no_vote(age_range, sex=None):
    # 采用不投票结果统计错误
    # 初始化每个取值的计数器
    all_counts = {
        'initial':{},
        'consonant':{},
        'tone':{},
    }
    for key in ['initial', 'consonant', 'tone']:
        for target in all_keys[key]:
            all_counts[key][target] = {}
            for spoken in all_keys[key]:
                all_counts[key][target][spoken] = 0
        
    subject_info = json.load(open('data/subject_id2info.json'))
    all_char_info = json.load(open('data/all_char_infos.json'))
    
    # 根据所有结果计数
    for subjectid, all_chars_user in all_char_info.items():
        # 性别过滤
        if sex is not None:
            if subject_info[subjectid]['sex'] != sex:
                continue
        # 忽略月龄在范围以外的
        age = subject_info[subjectid]['age_month']
        if age <= age_range[1] and age_range[0] <= age:
            for _, all_chars in all_chars_user.items():
                for char in all_chars:
                    for key in ['initial', 'consonant', 'tone']:
                        target = char['target'][key]
                        spoken = char['spoken'][key]
                        if target == '-':
                            continue
                        if target not in all_keys[key]:
                            # print(target)
                            target = '*'
                        if spoken not in all_keys[key]:
                            # print(spoken)
                            spoken = '*'
                        all_counts[key][target][spoken] += 1
    return all_counts

def analyze_age_group(vote=False, age_range=(0, 1200), sex=None):
    if vote:
        all_counts = count_vote(age_range, sex=sex)
    else:
        all_counts = count_no_vote(age_range, sex=sex)
    # 统计正确率错误率
    all_probs = {}
    for key in ['initial', 'consonant', 'tone']:
        all_probs[key] = copy.deepcopy(all_counts[key])
        for target, count in all_counts[key].items():
            total_num = sum([c for _,c in count.items()])
            for spoken, c in count.items():
                all_probs[key][target][spoken] = c / total_num if total_num != 0 else 0.0
    
    # 绘制混淆矩阵
    age_notation = f"{age_range[0]}-{age_range[1]}"
    json.dump(all_counts, open(f'values/{age_notation}_count_{"投票" if vote else "不投票"}_{sex if sex is not None else "both"}.json', 'w'))
    draw_heatmap(all_probs['consonant'], threshold=threshold['结构'], split_pos=split_pos['结构'], 
                    x_ticks=all_keys['结构'][:-1],
                    y_ticks=[all_keys['结构'][i] for i in range(len(all_keys['结构'])-1, -1, -1)],
                    discard_diag=True,
                    font_size=font_size[key],
                    num_format=num_format['结构'],
                    size_t=fig_size['结构'], dpi=dpis['结构'],
                    save_path=f'figs/结构_{age_notation}_prob_{"投票" if vote else "不投票"}_{sex if sex is not None else "both"}.png',
                    format_save='png')
    for key in ['initial', 'consonant', 'tone']:
        draw_heatmap(all_probs[key], threshold=threshold[key], split_pos=split_pos[key], 
                     x_ticks=all_keys[key][:-1],
                     y_ticks=[all_keys[key][i] for i in range(len(all_keys[key])-1, -1, -1)],
                     discard_diag=True,
                     font_size=font_size[key],
                     num_format=num_format[key],
                     size_t=fig_size[key], dpi=dpis[key],
                     save_path=f'figs/{key}_{age_notation}_prob_{"投票" if vote else "不投票"}_{sex if sex is not None else "both"}.png',
                     format_save='png')
        
        
analyze_age_group(vote=False, age_range=(0, 7200))
analyze_age_group(vote=False, age_range=(0,71))
analyze_age_group(vote=False, age_range=(72,1200))
analyze_age_group(vote=True, age_range=(0, 7200))
analyze_age_group(vote=True, age_range=(0,71))
analyze_age_group(vote=True, age_range=(72,1200))

analyze_age_group(vote=False, age_range=(0, 7200), sex='male')
analyze_age_group(vote=False, age_range=(0,71), sex='male')
analyze_age_group(vote=False, age_range=(72,1200), sex='male')
analyze_age_group(vote=True, age_range=(0, 7200), sex='male')
analyze_age_group(vote=True, age_range=(0,71), sex='male')
analyze_age_group(vote=True, age_range=(72,1200), sex='male')

analyze_age_group(vote=False, age_range=(0, 7200), sex='female')
analyze_age_group(vote=False, age_range=(0,71), sex='female')
analyze_age_group(vote=False, age_range=(72,1200), sex='female')
analyze_age_group(vote=True, age_range=(0, 7200), sex='female')
analyze_age_group(vote=True, age_range=(0,71), sex='female')
analyze_age_group(vote=True, age_range=(72,1200), sex='female')