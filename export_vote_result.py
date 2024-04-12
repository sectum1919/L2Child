import json

def is_same_opinion(opinions):
    return len(list(set(opinions))) == 1

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

def export_vote_result():
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
        for i in range(char_count):
            all_char_count += 1
            target_initials = [anno[i]['target']['initial'] for _, anno in annotations.items()]
            target_consonants = [anno[i]['target']['consonant'] for _, anno in annotations.items()]
            target_tones = [anno[i]['target']['tone'] for _, anno in annotations.items()]
            spoken_initials = [anno[i]['spoken']['initial'] for _, anno in annotations.items()]
            spoken_consonants = [anno[i]['spoken']['consonant'] for _, anno in annotations.items()]
            spoken_tones = [anno[i]['spoken']['tone'] for _, anno in annotations.items()]
            if is_same_opinion(target_initials) and is_same_opinion(target_consonants) and is_same_opinion(target_tones):
                spoken_initial_res = most_opinion(spoken_initials)
                spoken_consonant_res = most_opinion(spoken_consonants)
                spoken_tone_res = most_opinion(spoken_tones)
                if spoken_tone_res is not None and spoken_consonant_res is not None and spoken_initial_res is not None:
                    anno_results[subjectid].append({
                        "char": annotations[userids[0]][i]['char'],
                        "pinyin": annotations[userids[0]][i]['pinyin'],
                        "target": {
                            "initial": target_initials[0],
                            "consonant": target_consonants[0],
                            "tone": target_tones[0],
                        },
                        "spoken": {
                            "initial": spoken_initial_res,
                            "consonant": spoken_consonant_res,
                            "tone": spoken_tone_res
                        }
                    })
                    save_char_count += 1
    print(all_char_count, save_char_count)
    json.dump(anno_results, open('data/all_char_vote.json', 'w'), indent=4, ensure_ascii=False)
    
export_vote_result()