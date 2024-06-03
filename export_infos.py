import json

# 统计错误率等
# 只保留考察词以及确认儿童认识的
subjects = json.load(open('data/subject_id2info.json'))
all_anno_info = json.load(open('data/annoword_result_cslt_min.json'))

def analyze_one_word(data):
    word = []
    for i in range(len(data['content'])):
        # 真实文本
        target_hanzi = data['content'][i]
        if target_hanzi == ' ':
            continue
        target_pinyin = data['pyt'][i]
        target_phone = data['pinyin']['correct'][i].strip(' ').split(' ')
        target_shengmu, target_yunmu, target_shengdiao = "", "", ""
        if len(target_phone) == 3:
            target_shengmu, target_yunmu, target_shengdiao = target_phone
        elif len(target_phone) == 2:
            target_yunmu, target_shengdiao = target_phone
        else:
            print(data)
            print('why this happen?')
            print('*'*200)
        if target_shengmu == 'y' or target_shengmu == 'w':
            target_shengmu = '-'
        if target_yunmu == 'ii' or target_yunmu == 'iii':
            target_yunmu = 'i'
        if target_yunmu == 'iou':
            target_yunmu = 'iu'
        error_phone = data['pinyin']['error'][i].split(' ')
        spoken_shengmu, spoken_yunmu, spoken_shengdiao = target_shengmu, target_yunmu, target_shengdiao
        if len(error_phone) == 3:
            error_shengmu, error_yunmu, error_shengdiao = error_phone
            if error_shengmu != '-':
                spoken_shengmu = error_shengmu
            if error_yunmu != '-':
                spoken_yunmu = error_yunmu
            if error_shengdiao != '-':
                spoken_shengdiao = error_shengdiao
        else:
            print(data)
            print('why this happen?')
            print('*'*200)
        if spoken_yunmu == 'ii' or spoken_yunmu == 'iii':
            spoken_yunmu = 'i'
        if spoken_yunmu == 'iou':
            spoken_yunmu = 'iu'
        char = {
            'char': target_hanzi,
            'pinyin': target_pinyin,
            'target': {
                'initial': target_shengmu,
                'consonant': target_yunmu,
                'tone': target_shengdiao,
            },
            'spoken': {
                'initial': spoken_shengmu,
                'consonant': spoken_yunmu,
                'tone': spoken_shengdiao,
            }
        }
        word.append(char)
    return word

# 仅保留每个字对应的声母韵母声调目标与实际读音
all_chars_res = {}
for subjectid, annotations in all_anno_info.items():
    all_chars_res[subjectid] = {}
    for annotation in annotations:
        all_chars_res[subjectid][str(annotation['userid'])] = []

# 保留所有信息，包括起止时间
all_valid_infos = {}
for subjectid, annotations in all_anno_info.items():
    all_valid_infos[subjectid] = {}
    for annotation in annotations:
        all_valid_infos[subjectid][str(annotation['userid'])] = []

examinfo = json.load(open('data/examinfo.json'))

word_count = 0
char_count = 0
all_word_count = 0
all_char_count = 0
print(len(all_anno_info))
for subjectid, annotations in all_anno_info.items():
    # word_count = [len(a['anno_res']) for a in annotations]
    # print(word_count)
    for annotation in annotations:
        # 读取标注信息
        anno_user = str(annotation['userid'])
        anno_res = annotation['anno_res']
        exam_id = str(annotation['examid'])
        for i, word in enumerate(anno_res):
            all_word_count += 1
            all_char_count += len(word['data']['content'])
            isexamword = [0 if a['anno_res'][i]['data']['isexamword'] == 'no' else 1 for a in annotations]
            if sum(isexamword) < 3:
                continue
            # 跳过三个标注者标注的内容不一样的情况
            wordlength = [len(a['anno_res'][i]['data']['content']) for a in annotations]
            word_targ = [''.join(a['anno_res'][i]['data']['content']) for a in annotations]
            if len(list(set(wordlength))) != 1:
                continue
            if len(list(set(word_targ))) != 1:
                # print(list(set(word_targ)), word_targ)
                continue
            # added at 20240603 use real target phones for target
            for a in annotations:
                if word_targ[0] in examinfo['5-阶段五']:
                    info_correct = examinfo['5-阶段五'][word_targ[0]]
                elif word_targ[0] in examinfo['6-阶段六']:
                    info_correct = examinfo['6-阶段六'][word_targ[0]]
                else:
                    info_correct = None
                if info_correct is not None:
                    a['anno_res'][i]['data']['pyt'] = info_correct['py']
                    a['anno_res'][i]['data']['pinyin']['correct'] = [
                        (info_correct['sm'][i] if info_correct['sm'][i] != '零' else info_correct['sm'][i]) + ' ' + info_correct['ym'][i] + ' ' + str(info_correct['sd'][i])
                        for i in range(wordlength[0])
                    ]
            # 新增20240426 
            phone_targ = ['|'.join(a['anno_res'][i]['data']['pinyin']['correct']) for a in annotations]
            if len(list(set(phone_targ))) != 1:
                # print(list(set(word_targ)), word_targ)
                continue
            # 不需要管孩子是否认识（known）和是否有效（valid）
            # 是否有效这个字段没有任何意义
            word_info = analyze_one_word(word['data'])
            all_valid_infos[subjectid][anno_user].append({
                'start': word['start'],
                'end': word['end'],
                'known': word['data']['known'] if word['data']['known']!='idk' else 'notsure',
                'data': word_info,
            })
            word_count += 1
            char_count += len(word_info)
            for charidx, char in enumerate(word_info):
                all_chars_res[subjectid][anno_user].append(char)
print(word_count, char_count)
print(all_word_count, all_char_count)
json.dump(all_chars_res, open('data/all_char_infos.json', 'w'), ensure_ascii=False)
json.dump(all_valid_infos, open('data/all_valid_infos.json', 'w'), ensure_ascii=False)