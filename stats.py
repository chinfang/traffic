import pandas as pd

variables = ['發生月份', '天候名稱', '光線名稱',\
             '速限-第1當事者', '道路型態子類別名稱', '事故位置子類別名稱', '道路障礙-障礙物名稱', '道路障礙-視距名稱',\
             '號誌-號誌種類名稱', '號誌-號誌動作名稱', '車道劃分設施-分向設施大類別名稱',\
             '車道劃分設施-分道設施-快車道或一般車道間名稱',\
             '事故類型及型態大類別名稱', '事故類型及型態子類別名稱', '肇因研判大類別名稱-主要', '肇因研判子類別名稱-主要',\
             '當事者事故發生時年齡']
array_cols = ['當事者事故發生時年齡', '肇因研判大類別名稱-主要', '肇因研判子類別名稱-主要']

dfs = pd.DataFrame()
df_stats = pd.DataFrame()

for year in range(2018, 2024):
    filePath = './data/'+str(year)+'.parquet'
    df = pd.read_parquet(filePath)
    df['發生縣市'] = df['發生地點'].str[0:3]
    dfs = pd.concat([dfs, df])

# Value count for each category    
for var in variables:
    # stats country
    if var in array_cols:
        df_stat = dfs.explode(var).reset_index(drop=True).groupby(['發生季度', var]).size().sort_values()
    else:
        df_stat = dfs.groupby(['發生季度', var]).size().sort_values()
    df_stat = df_stat.reset_index()
    df_stat.columns = ['發生季度', 'value', 'count']
    df_stat['發生縣市'] = '全台'
    df_stat['因子'] = var
    df_stats = pd.concat([df_stats, df_stat])
    
    # stats cities
    if var in array_cols:
        df_stat = dfs.explode(var).reset_index(drop=True).groupby(['發生季度', '發生縣市', var]).size().sort_values()
    else:
        df_stat = dfs.groupby(['發生季度', '發生縣市', var]).size().sort_values()
    df_stat = df_stat.reset_index()
    df_stat.columns = ['發生季度', '發生縣市', 'value', 'count']
    df_stat['因子'] = var
    df_stats = pd.concat([df_stats, df_stat])

df_stats[['發生季度', 'value']] = df_stats[['發生季度', 'value']].astype(str)
outputPath = './data/stats.parquet'
df_stats.to_parquet(outputPath)   