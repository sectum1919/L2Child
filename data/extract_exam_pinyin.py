import csv
import json
import pandas as pd
df = pd.read_csv('datailed_infos.csv', encoding='gbk')
dfinfo = json.loads(df.to_json())
print(dfinfo.keys())
print(len(dfinfo['cpy']))

examinfo = {}
cid = 0
# print(dfinfo['测试试卷号'].keys())
while True:
    if cid >= 28033:
        break
    exam = dfinfo['测试试卷号'][str(cid)]
    if exam not in examinfo:
        examinfo[exam] = {}
    czh = dfinfo['词'][str(cid)]
    if czh in examinfo[exam]:
        cid += 1
        continue
    if cid+1 < 28033 and dfinfo['词序'][str(cid+1)] == 2 and dfinfo['pos'][str(cid)] == '2#1' and dfinfo['pos'][str(cid+1)] == '2#2':
        czh = dfinfo['词'][str(cid)]
        cpy = [dfinfo['zpy'][str(cid)], dfinfo['zpy'][str(cid+1)]]
        csm = [dfinfo['zsm'][str(cid)], dfinfo['zsm'][str(cid+1)]]
        cym = [dfinfo['zym'][str(cid)], dfinfo['zym'][str(cid+1)]]
        csd = [dfinfo['zsd'][str(cid)], dfinfo['zsd'][str(cid+1)]]
        examinfo[exam][czh] = {
            'py': cpy,
            'sm': csm,
            'ym': cym,
            'sd': csd,
        }
        cid += 2
        print(czh, examinfo[exam][czh])
    elif dfinfo['词序'][str(cid+1)] == 1 and dfinfo['pos'][str(cid)] == '1#1':
        czh = dfinfo['词'][str(cid)]
        cpy = [dfinfo['zpy'][str(cid)]]
        csm = [dfinfo['zsm'][str(cid)]]
        cym = [dfinfo['zym'][str(cid)]]
        csd = [dfinfo['zsd'][str(cid)]]
        examinfo[exam][czh] = {
            'py': cpy,
            'sm': csm,
            'ym': cym,
            'sd': csd,
        }
        cid += 1
        print(czh, examinfo[exam][czh])
    else:
        cid+=1
        
json.dump(examinfo, open('examinfo.json', 'w'), indent=4, ensure_ascii=False)