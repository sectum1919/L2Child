import json

# 第二批数据全都是2023年2月份~3月份录制的，统一按照2月份计算测试月龄
def cal_age(birthday):
    year, month, day = [int(s) for s in birthday.split('-')]
    return (2023 - year) * 12 + 2 - month

# 直接读取第一批数据的儿童信息
import pandas as pd
df = pd.read_csv('儿童清单.csv', encoding='gbk')
json_str = df.to_json(orient='records', force_ascii=False)
json_data = json.loads(json_str)
subjectno2subject = {}
for subject in json_data:
    subjectno = subject['儿童编号']
    subjectno2subject[subjectno] = {
        'subjectno': subjectno,
        'sex': 'male' if subject['性别'] == '男' else 'female',
        'age_month': int(subject['测试月龄']),
        'month_start_speak': int(subject['开始说话月龄']),
        'mother_hometown': subject['母亲籍贯'],
        'father_hometown': subject['父亲籍贯'],
    }
    
all_word_info = json.load(open('annoword_result_cslt_min.json'))
subjects_info = json.load(open('subjects.json'))
subjectid2subjectno = {}
subjectid2subject = {}
for row in subjects_info[0]['rows']:
    subjectid = row[0]
    if str(subjectid) not in all_word_info:
        continue
    subjectno = row[2]
    if subjectno.startswith('XJYL-MLD'):
        subjectno = '-'.join(subjectno.split('-')[:-1])
        subjectid2subject[subjectid] = subjectno2subject[subjectno]
    else:
        sex = row[4]
        age = cal_age(row[5])
        subjectid2subject[subjectid] = {
            'subjectno': subjectno,
            'sex': sex,
            'age_month': age,
            'month_start_speak': int(row[7]),
            'mother_hometown': row[9],
            'father_hometown': row[8],
        }
    subjectid2subjectno[subjectid] = subjectno
json.dump(subjectid2subjectno, open('subject_id2no.json', 'w'), indent=4, ensure_ascii=False)
json.dump(subjectid2subject, open('subject_id2info.json', 'w'), indent=4, ensure_ascii=False)
