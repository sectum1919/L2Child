import matplotlib.pyplot as plt
# all data
# {'initials': {3: 14, 2: 573, 1: 23417}, 'consonants': {3: 24, 2: 676, 1: 23873}, 'tones': {3: 46, 2: 1766, 1: 22761}}
# where same opinion and == target are exclude
# {'initials': {3: 14, 2: 573, 1: 43}, 'consonants': {3: 24, 2: 676, 1: 52}, 'tones': {3: 46, 2: 1766, 1: 229}}
# 数据
labels = ['1', '2', '3']
sizes_1 = [23417, 573, 14]
sizes_2 = [23873, 676, 24]
sizes_3 = [22761, 1766, 46]
sizes_4 = [43, 573, 14]
sizes_5 = [52, 676, 24]
sizes_6 = [229, 1766, 46]

explode = [0, 0.1, 0.2]

# 创建一个figure对象和三个子图
fig, axs = plt.subplots(2, 3, figsize=(15, 15))

# 绘制第一个饼图
axs[0, 0].pie(sizes_1, labels=labels, explode=explode, autopct='%1.1f%%', startangle=0)
axs[0, 0].set_title('Initials')

# 绘制第二个饼图
axs[0, 1].pie(sizes_2, labels=labels, explode=explode, autopct='%1.1f%%', startangle=0)
axs[0, 1].set_title('Consonants')

# 绘制第三个饼图
axs[0, 2].pie(sizes_3, labels=labels, explode=explode, autopct='%1.1f%%', startangle=0)
axs[0, 2].set_title('Tones')

# 绘制第4个饼图
axs[1, 0].pie(sizes_4, labels=labels, autopct='%1.1f%%', startangle=0)
axs[1, 0].set_title('Initials')

# 绘制第5个饼图
axs[1, 1].pie(sizes_5, labels=labels, autopct='%1.1f%%', startangle=0)
axs[1, 1].set_title('Consonants')

# 绘制第6个饼图
axs[1, 2].pie(sizes_6, labels=labels, autopct='%1.1f%%', startangle=0)
axs[1, 2].set_title('Tones')
# 调整布局
plt.tight_layout()
# 显示图形
plt.suptitle('# of opinions')
plt.savefig('statics/pie.png')


import matplotlib.pyplot as plt
import numpy as np
import json
entropys = json.load(open('/work2/cchen/code/L2Child/users_entropy_origin.json'))
# 数据
N = 3  # 每组内的柱子数量
ind = np.arange(N)  # 柱子的索引
# 柱子的宽度
width = 0.2
# 绘图
fig, axes = plt.subplots(1, 3, figsize=(15,7))

for i, type in enumerate(['initial', 'consonant', 'tone']):
        
    data1 = [entropys['0-71']['both'][type][user] for user in ['HX', 'HY', 'HZ']]
    data2 = [entropys['72-1200']['both'][type][user] for user in ['HX', 'HY', 'HZ']]
    data3 = [entropys['0-1200']['both'][type][user] for user in ['HX', 'HY', 'HZ']]

    rects1 = axes[i].bar(ind, data1, width, color='r', label='User A')
    rects2 = axes[i].bar(ind + width, data2, width, color='g', label='User B')
    rects3 = axes[i].bar(ind + 2*width, data3, width, color='b', label='User C')

    # 添加标签、标题和图例
    axes[i].set_xlabel('Users')
    axes[i].set_ylabel('Values')
    if type == 'tone':
        axes[i].set_ylim(1.0, 2.0)
    else:    
        axes[i].set_ylim(2.5, 3.5)
    axes[i].set_title(type)
    axes[i].set_xticks(ind + width)
    axes[i].set_xticklabels(('0-71', '72-1200', '0-1200'))
    axes[i].legend()

plt.savefig('statics/bar.png')