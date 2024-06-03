# -*- encoding: utf-8 -*-
'''
Filename         :entropy_analyze_annotation.py
Description      :计算每个标注者的熵和互信息
Time             :2024/04/26 17:04:21
Author           :chenchen
'''
import json
import numpy as np
import copy

from analyze_common_utils import *
import time

all_annotations2idx = {
    key:{
        f"{k1}-{k2}": i * len(all_keys[key]) + j
        for i, k1 in enumerate(all_keys[key])
        for j, k2 in enumerate(all_keys[key])
    }
    for key in ['initial', 'consonant', 'tone']
}

# print(all_annotations2idx)

def joint_entropy(x, y, z):
    """Computes the joint entropy of three discrete random variables.

    Args:
        x: A numpy array of values for the first random variable.
        y: A numpy array of values for the second random variable.
        z: A numpy array of values for the third random variable.

    Returns:
        The joint entropy of the three random variables.
    """

    # Check that the inputs are valid.
    if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray) or not isinstance(z, np.ndarray):
        raise ValueError("Inputs must be numpy arrays.")
    if x.shape[0] != y.shape[0] or x.shape[0] != z.shape[0]:
        raise ValueError("Inputs must have the same length.")

    # Compute the joint probability distribution.
    joint_probs = np.zeros((len(np.unique(x)), len(np.unique(y)), len(np.unique(z))))
    for i in range(len(x)):
        joint_probs[x[i], y[i], z[i]] += 1
    joint_probs /= len(x)

    # Compute the joint entropy.
    joint_entropy = -np.nansum(joint_probs * np.log(joint_probs))

    return joint_entropy

def joint_entropy_xyz(labelx, labely, labelz, x_cluster_count, y_cluster_count, z_cluster_count):
    print(len(labelx), len(labely), len(labelz))
    # p(x,y) H(X,Y)
    countxy = np.zeros([x_cluster_count, y_cluster_count])
    for lx, ly in zip(labelx, labely):
        countxy[lx][ly] += 1
    probxy = np.float128(countxy) / len(labelx)
    logpxy = np.ma.log(probxy).filled(0)
    HXY = -np.sum(countxy*np.array(logpxy)) / len(labelx)
    
    # p(x,z) H(X,Z)
    countxz = np.zeros([x_cluster_count, z_cluster_count])
    for lx, lz in zip(labelx, labelz):
        countxz[lx][lz] += 1
    probxz = np.float128(countxz) / len(labelx)
    logpxz = np.ma.log(probxz).filled(0)
    HXZ = -np.sum(countxz*np.array(logpxz)) / len(labelx)
    
    # p(z,y) H(Z,Y)
    countzy = np.zeros([z_cluster_count, y_cluster_count])
    for lz, ly in zip(labelz, labely):
        countzy[lz][ly] += 1
    probzy = np.float128(countzy) / len(labelz)
    logpzy = np.ma.log(probzy).filled(0)
    HZY = -np.sum(countzy*np.array(logpzy)) / len(labelx)
    
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
    
    # p(z) H(z)
    countz = np.array([0 for _ in range(z_cluster_count)])
    for lz in labelz:
        countz[lz] += 1
    probz = np.float128(countz) / len(labelz)
    logpz = np.ma.log(probz).filled(0)
    HZ = -np.sum(countz*np.array(logpz)) / len(labelx)
    
    # p(x,y,z) H(x,y,z)
    countxyz = np.zeros([x_cluster_count, y_cluster_count, z_cluster_count])
    for i in range(len(labelx)):
        lx, ly, lz = labelx[i], labely[i], labelz[i]
        countxyz[lx][ly][lz] += 1
    probxyz = np.float128(countxyz) / len(labelx)
    logpxyz = np.ma.log(probxyz).filled(0)
    HXYZ = -np.nansum(countxyz*np.array(logpxyz)) / len(labelx)
    
    return HXY, HXZ, HZY, HX, HY, HZ, HXYZ

def load_all_annotation(subject_info, all_char_info, annouser, age_range=(0,1200), sex=None):
    all_annotations = {
        'initial':[],
        'consonant':[],
        'tone':[],
    }
    # 根据所有结果计数
    for subjectid, all_chars_user in all_char_info.items():
        # 性别过滤
        if sex is not None:
            if subject_info[subjectid]['sex'] != sex:
                continue
        # 忽略月龄在范围以外的
        age = subject_info[subjectid]['age_month']
        if age <= age_range[1] and age_range[0] <= age:
            for userid, all_chars in all_chars_user.items():
                if userid != annouser:
                    continue
                for i, char in enumerate(all_chars):
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
                        all_annotations[key].append(f"{target}-{spoken}")
    return all_annotations

def entropy_annusers(datasource):
    subject_info = json.load(open('data/subject_id2info.json'))
    if datasource == 'origin':
        all_char_info = json.load(open('data/all_char_infos.json'))
    else:
        all_char_info = json.load(open('data/all_char_different_opinion.json'))
    
    all_annotations_users = {}
    for userid in ['20', '21', '30']:
        all_annotations_users[userid] = {}
        for age_group in [(0,71), (72, 1200), (0, 1200)]:
        # for age_group in [(0, 1200)]:
            all_annotations_users[userid][age_group] = {}
            # for sex in [None]:
            for sex in ['male', 'female', None]:
                all_annotations_users[userid][age_group][sex] = load_all_annotation(subject_info, all_char_info, userid, age_range=age_group, sex=sex)

    print('load data')
    res = {}
    for age_group in [(0,71), (72, 1200), (0, 1200)]:
        age_notation = f"{age_group[0]}-{age_group[1]}"
        res[age_notation] = {}
        for sex in ['male', 'female', None]:
            res[age_notation][sex if sex is not None else 'both'] = {}
            for key in ['initial', 'consonant', 'tone']:
                res[age_notation][sex if sex is not None else 'both'][key] = {}
                print(age_group, sex, key)
                all_annos = all_annotations_users['20'][age_group][sex][key] + all_annotations_users['21'][age_group][sex][key] + all_annotations_users['30'][age_group][sex][key]
                # print(all_annos[0])
                all_annos = list(set(all_annos))
                all_annos = {c:i for i,c in enumerate(all_annos)}
                st = time.time()
                HXY, HXZ, HYZ, HX, HY, HZ, HXYZ = joint_entropy_xyz(np.array([all_annos[c] for c in all_annotations_users['20'][age_group][sex][key]]),
                                                                    np.array([all_annos[c] for c in all_annotations_users['21'][age_group][sex][key]]),
                                                                    np.array([all_annos[c] for c in all_annotations_users['30'][age_group][sex][key]]),
                                                                    len(all_annos),
                                                                    len(all_annos),
                                                                    len(all_annos),
                                                                    )
                # print(age_group, sex)
                print([round(x, 4) for x in [HXY, HXZ, HYZ, HX, HY, HZ, HXYZ]])
                print('time usage:', time.time()-st)
                res[age_notation][sex if sex is not None else 'both'][key] = {
                    'HX': float(HX),
                    'HY': float(HY),
                    'HZ': float(HZ),
                    'HXY': float(HXY),
                    'HYZ': float(HYZ),
                    'HXZ': float(HXZ),
                    'HXYZ': float(HXYZ),
                    'MIXY': float(HX + HY - HXY),
                    'MIYZ': float(HZ + HY - HYZ),
                    'MIXZ': float(HX + HZ - HXZ),
                    'MIXYZ': float(HXYZ + HY + HX + HZ - HYZ - HXY - HXZ),
                }
    json.dump(res, open(f'users_entropy_{datasource}.json', 'w'), indent=4, ensure_ascii=False)

entropy_annusers(datasource='origin')
entropy_annusers(datasource='diffopinion')