import csv
import pandas as pd
import json

all_char_info = json.load(open('data/all_char_infos.json'))
all_char_count = 0
with open('all_char_info.csv', 'w') as fp:
    fp.write(f"id,spkid,target_initials_1,target_initials_2,target_initials_3,spoken_initials_1,spoken_initials_2,spoken_initials_3,target_consonants_1,target_consonants_2,target_consonants_3,spoken_consonants1,spoken_consonants2,spoken_consonants3,target_tones_1,target_tones_2,target_tones_3,spoken_tones_1,spoken_tones_2,spoken_tones_3\n")
    for subjectid, annotations in all_char_info.items():
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
            content = [str(all_char_count), str(subjectid)] + target_initials + spoken_initials + target_consonants + spoken_consonants + target_tones + spoken_tones
            fp.write(','.join(content) + '\n')