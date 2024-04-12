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
                

def count_vote(age_range):
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
        
    subject_info = json.load(open('data/subject_id2info.json'))
    all_char_info = json.load(open('data/all_char_vote.json'))
    
    # 根据所有结果计数
    for subjectid, all_chars in all_char_info.items():
        age = subject_info[subjectid]['age_month']
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
    

def count_no_vote(age_range):
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
        for _, all_chars in all_chars_user.items():
            age = subject_info[subjectid]['age_month']
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

def analyze_age_group(vote=False, age_range=(0, 1200)):
    if vote:
        all_counts = count_vote(age_range)
    else:
        all_counts = count_no_vote(age_range)
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
    draw_heatmap(all_probs['consonant'], threshold=threshold['结构'], split_pos=split_pos['结构'], 
                    x_ticks=all_keys['结构'][:-1],
                    y_ticks=[all_keys['结构'][i] for i in range(len(all_keys['结构'])-1, -1, -1)],
                    discard_diag=True,
                    font_size=font_size[key],
                    num_format=num_format['结构'],
                    size_t=fig_size['结构'], dpi=dpis['结构'],
                    save_path=f'figs/结构_{age_notation}_prob_{"投票" if vote else "不投票"}.png',
                    format_save='png')
    for key in ['initial', 'consonant', 'tone']:
        draw_heatmap(all_probs[key], threshold=threshold[key], split_pos=split_pos[key], 
                     x_ticks=all_keys[key][:-1],
                     y_ticks=[all_keys[key][i] for i in range(len(all_keys[key])-1, -1, -1)],
                     discard_diag=True,
                     font_size=font_size[key],
                     num_format=num_format[key],
                     size_t=fig_size[key], dpi=dpis[key],
                     save_path=f'figs/{key}_{age_notation}_prob_{"投票" if vote else "不投票"}.png',
                     format_save='png')
        
        
analyze_age_group(vote=False, age_range=(0, 7200))
analyze_age_group(vote=False, age_range=(0,71))
analyze_age_group(vote=False, age_range=(72,1200))


analyze_age_group(vote=True, age_range=(0, 7200))
analyze_age_group(vote=True, age_range=(0,71))
analyze_age_group(vote=True, age_range=(72,1200))