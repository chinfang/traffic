import requests
import numpy as np
import pandas as pd
import urllib.parse
from pymongo import MongoClient

user = 'kiang'
repo = 'NPA_TMA'

url = 'https://api.github.com/repos/{}/{}/git/trees/master?recursive=1'.format(user, repo)
r = requests.get(url)
res = r.json()

for year in range(2018, 2024):
    for type in ['a1', 'a2']:
        dfs = pd.DataFrame()
        for file in res['tree']:
            if 'data/'+str(year) in file['path'].lower() and 'csv' in file['path'].lower() and type in file['path'].lower():
                print('process ', file['path'])

                url = 'https://github.com/kiang/NPA_TMA/raw/master/'+urllib.parse.quote(file['path'])
                try:
                    df = pd.read_csv(url, dtype={'發生年度': str})
                except:
                    pass
                dfs = pd.concat([dfs, df])

    print('process age')
    # Process age
    dfs['當事者事故發生時年齡_bin'] = pd.cut(dfs['當事者事故發生時年齡'], [0, 12, 17, 24, 65, np.inf], 
    labels=['0-12', '13-17', '18-24', '25-64', '>65'], include_lowest=True)
    dfs['當事者事故發生時年齡_bin'] = dfs['當事者事故發生時年齡_bin'].values.add_categories('未知')
    dfs['當事者事故發生時年齡_bin'] = dfs['當事者事故發生時年齡_bin'].fillna('未知')
    dfs['當事者事故發生時年齡'] = dfs['當事者事故發生時年齡_bin']
    dfs.drop(['當事者事故發生時年齡_bin'], axis=1, inplace=True)

    # Drop missing location
    print('process location')
    dfs = dfs[(dfs['緯度'].notna()) & (dfs['經度'].notna())]

    # Format columns
    dfs['發生月份'] = dfs['發生月份'].astype(int).astype(str).str.zfill(2)
    dfs[['速限-第1當事者']] = dfs[['速限-第1當事者']].apply(lambda x: x.astype('str'))
    dfs['date'] = dfs['發生年度'] + dfs['發生月份']
    dfs['發生季度'] = pd.PeriodIndex(pd.to_datetime(dfs['date'], format='%Y%m'), freq='Q')
    dfs = dfs.reset_index()
    # dfs.drop_duplicates(inplace=True)

    # Group columns
    group_cols = ['發生年度', '發生季度', '發生月份', '發生地點', '天候名稱', '光線名稱',\
                '速限-第1當事者', '道路型態子類別名稱', '事故位置子類別名稱', '道路障礙-障礙物名稱', '道路障礙-視距名稱',\
                '號誌-號誌種類名稱', '號誌-號誌動作名稱', '車道劃分設施-分向設施大類別名稱',\
                '車道劃分設施-分道設施-快車道或一般車道間名稱',\
                '事故類型及型態大類別名稱', '事故類型及型態子類別名稱', '死亡受傷人數', '經度', '緯度']
    join_cols = ['當事者事故發生時年齡', '肇因研判大類別名稱-主要', '肇因研判子類別名稱-主要']
    dfs = dfs[group_cols+join_cols].groupby(group_cols).agg(list).reset_index()

    # Write output
    outputPath = './data/'+str(year)+'.parquet'
    print('write parquet', outputPath)
    dfs.to_parquet(outputPath)