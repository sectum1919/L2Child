# -*- encoding: utf-8 -*-
'''
Filename         :analyze_subject.py
Description      :根据投票/汇总结果，为每一个孩子绘制热力图
Time             :2024/04/26 16:59:00
Author           :chenchen
'''


import json
import numpy as np
import copy

from analyze_common_utils import *

def count_vote(subjectid):
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
    all_char_info = json.load(open('data/all_char_vote.json'))
    # 根据所有结果计数
    all_chars = all_char_info[subjectid]
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
    

def count_no_vote(subjectid):
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
    all_char_info = json.load(open('data/all_char_infos.json'))
    all_chars_user = all_char_info[subjectid]
    # 根据所有结果计数
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

def analyze_subject(subjectid, vote=False):        
    subject_info = json.load(open('data/subject_id2info.json', encoding='gbk'))
    if vote:
        all_counts = count_vote(subjectid)
    else:
        all_counts = count_no_vote(subjectid)
    # 统计正确率错误率
    all_probs = {}
    for key in ['initial', 'consonant', 'tone']:
        all_probs[key] = copy.deepcopy(all_counts[key])
        for target, count in all_counts[key].items():
            total_num = sum([c for _,c in count.items()])
            for spoken, c in count.items():
                all_probs[key][target][spoken] = c / total_num if total_num != 0 else 0.0
    
    # 绘制混淆矩阵
    json.dump(all_counts, open(f'subjects/count_{"投票" if vote else "不投票"}_{subject_info[subjectid]["subjectno"]}.json', 'w'))
    draw_heatmap(all_probs['consonant'], threshold=threshold['结构'], split_pos=split_pos['结构'], 
                    x_ticks=all_keys['结构'][:-1],
                    y_ticks=[all_keys['结构'][i] for i in range(len(all_keys['结构'])-1, -1, -1)],
                    discard_diag=True,
                    font_size=font_size[key],
                    num_format=num_format['结构'],
                    size_t=fig_size['结构'], dpi=dpis['结构'],
                    save_path=f'subjects/结构_prob_{"投票" if vote else "不投票"}_{subject_info[subjectid]["subjectno"]}.png',
                    format_save='png')
    for key in ['initial', 'consonant', 'tone']:
        draw_heatmap(all_probs[key], threshold=threshold[key], split_pos=split_pos[key], 
                     x_ticks=all_keys[key][:-1],
                     y_ticks=[all_keys[key][i] for i in range(len(all_keys[key])-1, -1, -1)],
                     discard_diag=True,
                     font_size=font_size[key],
                     num_format=num_format[key],
                     size_t=fig_size[key], dpi=dpis[key],
                     save_path=f'subjects/{key}_prob_{"投票" if vote else "不投票"}_{subject_info[subjectid]["subjectno"]}.png',
                     format_save='png')
        
subjects = json.load(open('data/subject_id2info.json', encoding='gbk'))
for subjectid in subjects.keys():
    analyze_subject(subjectid=subjectid)