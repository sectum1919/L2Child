# -*- encoding: utf-8 -*-
'''
Filename         :entropy_analyze.py
Description      :根据年龄分组统计结果，计算每个phoneme的发音概率分布/错误概率分布的熵
Time             :2024/04/26 17:00:26
Author           :chenchen
'''


import numpy as np
import torch
import json
import copy


def entropy(count):
    countx = np.float128([c for k,c in count.items()])
    if np.sum(countx) < 1:
        return 0.0
    probx = np.float128(countx) / np.sum(countx)
    logpx = np.ma.log(probx).filled(0)
    HX = -np.sum(countx*np.array(logpx)) / np.sum(countx)
    return HX
    
def joint_entropy_xy(labelx, labely, x_cluster_count, y_cluster_count):
    
    # p(x,y) H(X,Y)
    countxy = np.zeros([x_cluster_count, y_cluster_count])
    for lx, ly in zip(labelx, labely):
        countxy[lx][ly] += 1
    probxy = np.float128(countxy) / len(labelx)
    logpxy = np.ma.log(probxy).filled(0)
    HXY = -np.sum(countxy*np.array(logpxy)) / len(labelx)
    
    # p(x) H(X)
    countx = np.array([0 for _ in range(x_cluster_count)])
    for lx in labelx:
        countx[lx] += 1
    probx = np.float128(countx) / len(labelx)
    logpx = np.ma.log(probx).filled(0)
    HX = -np.sum(countx*np.array(logpx)) / len(labelx)
    
    # p(y) H(y)
    county = np.array([0 for _ in range(y_cluster_count)])
    for ly in labely:
        county[ly] += 1
    proby = np.float128(county) / len(labely)
    logpy = np.ma.log(proby).filled(0)
    HY = -np.sum(county*np.array(logpy)) / len(labelx)
    
    return HXY, HX, HY

res = {}
for static in ['投票', '不投票']:
    res[static] = {}
    for age_group in ['0-7200', '72-1200', '0-71']:
        res[static][age_group] = {}
        for sex in ['both', 'male', 'female']:
            res[static][age_group][sex] = {}
            count = json.load(open(f"values/{age_group}_count_{static}_{sex}.json"))
            for key in ['initial', 'consonant', 'tone']:
                res[static][age_group][sex][key] = {}
                value = count[key]
                all_phones = len(value.keys())
                for phone, c in value.items():
                    H_ALL = float(entropy(c))
                    c_err = copy.deepcopy(c)
                    c_err[phone] = 0
                    H_ERR = float(entropy(c_err))
                    res[static][age_group][sex][key][phone] = {
                        'all': H_ALL,
                        'err': H_ERR,
                        'acc': (c[phone] / sum([v for k,v in c.items()])) if sum([v for k,v in c.items()]) != 0 else 1,
                        'count': sum([v for k,v in c.items()]),
                        'error': sum([v for k,v in c.items()]) - c[phone],
                    }
                value_err = copy.deepcopy(value)
                count_err = {}
                for phone, c in value_err.items():
                    c[phone] = 0
                    for p, v in c.items():
                        count_err[f"{phone}_{p}"] = v
                count_all = {}
                for phone, c in value.items():
                    for p, v in c.items():
                        count_all[f"{phone}_{p}"] = v
                H_ERR = float(entropy(count_err))
                H_ALL = float(entropy(count_all))
                res[static][age_group][sex][key]['all_distrib'] = {
                    'all': H_ALL,
                    'err': H_ERR,
                    'acc':   (sum([v for k,v in count_all.items()]) - sum([v for k,v in count_err.items()])) / sum([v for k,v in count_all.items()]),
                    'count': sum([v for k,v in count_all.items()]),
                    'error': sum([v for k,v in count_err.items()]),
                }
                print({k:round(v,4) for k,v in res[static][age_group][sex][key]['all_distrib'].items()}, static, age_group, sex, key)
json.dump(res, open('detailed_entropy.json', 'w'), indent=4, ensure_ascii=False)