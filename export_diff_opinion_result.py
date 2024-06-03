import json

def is_same_opinion(opinions):
    return len(list(set(opinions))) == 1

def is_different_opinion(opinions):
    return len(list(set(opinions))) != 1

def most_opinion(opinions):
    count = {}
    for op in opinions:
        if op not in count:
            count[op] = 0
        count[op] += 1
    for op, cnt in count.items():
        if cnt >= 2:
            return op
    return None

def export_different_opinion_result():
    # 投票结果分布
    count_json = {
         'initials': {3:0,2:0,1:0},
         'consonants': {3:0,2:0,1:0},
         'tones': {3:0,2:0,1:0},
    }
    char_infos = json.load(open('data/all_char_infos.json'))
    # 输出投票结果
    save_char_count = 0
    all_char_count = 0
    anno_results = {}
    # 遍历儿童
    for subjectid, annotations in char_infos.items():
        anno_results[subjectid] = []
        # 遍历三个标注者
        userids = [userid for userid, _ in annotations.items()]
        char_count = len(annotations[userids[0]])
        valid_idx = []
        for i in range(char_count):
            all_char_count += 1
            target_initials = [anno[i]['target']['initial'] for _, anno in annotations.items()]
            target_consonants = [anno[i]['target']['consonant'] for _, anno in annotations.items()]
            target_tones = [anno[i]['target']['tone'] for _, anno in annotations.items()]
            spoken_initials = [anno[i]['spoken']['initial'] for _, anno in annotations.items()]
            spoken_consonants = [anno[i]['spoken']['consonant'] for _, anno in annotations.items()]
            spoken_tones = [anno[i]['spoken']['tone'] for _, anno in annotations.items()]
            if is_same_opinion(target_initials) and is_same_opinion(target_consonants) and is_same_opinion(target_tones):
                if not (len(list(set(spoken_initials))) == 1 and (spoken_initials[0] == '-' or spoken_initials[0] == target_initials[0])):
                    count_json['initials'][len(list(set(spoken_initials)))] += 1
                if not (len(list(set(spoken_consonants))) == 1 and (spoken_consonants[0] == '-' or spoken_consonants[0] == target_consonants[0])):
                    count_json['consonants'][len(list(set(spoken_consonants)))] += 1
                if not (len(list(set(spoken_tones))) == 1 and (spoken_tones[0] == '-' or spoken_tones[0] == target_tones[0])):
                    count_json['tones'][len(list(set(spoken_tones)))] += 1
                if is_different_opinion(spoken_initials) or is_different_opinion(spoken_consonants) or is_different_opinion(spoken_tones):
                    valid_idx.append(i)
                    save_char_count += 1
        anno_results[subjectid] = {userid:[a for i,a in enumerate(annotation) if i in valid_idx] for userid, annotation in annotations.items()}           
    print(all_char_count, save_char_count)
    json.dump(anno_results, open('data/all_char_different_opinion.json', 'w'), indent=4, ensure_ascii=False)
    print(count_json)
export_different_opinion_result()