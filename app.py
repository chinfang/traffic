import leafmap
import pandas as pd
import streamlit as st
import altair as alt
import leafmap.foliumap as leafmap
import numpy as np
import xyzservices.providers as xyz

cols = ['發生年度', '發生月份', '發生地點', '天候名稱', '光線名稱',\
             '速限-第1當事者', '道路型態子類別名稱', '事故位置子類別名稱', '道路障礙-障礙物名稱', '道路障礙-視距名稱',\
             '號誌-號誌種類名稱', '號誌-號誌動作名稱', '車道劃分設施-分向設施大類別名稱',\
             '車道劃分設施-分道設施-快車道或一般車道間名稱',\
             '事故類型及型態大類別名稱', '事故類型及型態子類別名稱', '肇因研判大類別名稱-主要', '肇因研判子類別名稱-主要',\
             '當事者事故發生時年齡', '經度', '緯度']
variables = ['天候名稱', '光線名稱',\
             '速限-第1當事者', '道路型態子類別名稱', '事故位置子類別名稱', '道路障礙-障礙物名稱', '道路障礙-視距名稱',\
             '號誌-號誌種類名稱', '號誌-號誌動作名稱', '車道劃分設施-分向設施大類別名稱',\
             '車道劃分設施-分道設施-快車道或一般車道間名稱',\
             '事故類型及型態大類別名稱', '事故類型及型態子類別名稱', '肇因研判大類別名稱-主要', '肇因研判子類別名稱-主要',\
             '當事者事故發生時年齡']
cityList = ['基隆市', '臺北市', '新北市', '桃園市', '新竹市', '新竹縣', '苗栗縣', '臺中市',
            '彰化縣', '南投縣', '雲林縣', '嘉義市','嘉義縣', '臺南市', '高雄市', '屏東縣',
            '宜蘭縣', '花蓮縣', '臺東縣' '澎湖縣', '金門縣', '連江縣']

xmin=119
xmax=123
ymin=20
ymax=26

# Load data
df = pd.read_parquet("./data/2022.parquet")
df = df[(df['經度']>xmin) & (df['經度']<xmax) & (df['緯度']>ymin) & (df['緯度']<ymax)][cols]

# Set streamlit
st.set_page_config(
    page_title="台灣交通熱點地圖",
    page_icon="🔥",
    layout="wide")

st.sidebar.header('台灣交通熱點地圖')
# cities = np.append('全台', cityList)
city = st.sidebar.selectbox('發生地點:', cityList, index=1)
variable = st.sidebar.selectbox('因子類別:', variables, index=4)
options = np.append('全部', df[variable].unique())
option = st.sidebar.selectbox('因子名稱:', options, index=0)

tab1, tab2 = st.tabs(["地圖", "統計"])

with tab2:
    df_stats = pd.read_parquet('./data/stats.parquet')
    chart_data = df_stats[(df_stats['因子']==variable) & (df_stats['發生縣市']==city)].reset_index(drop=True)
    c = alt.Chart(chart_data).mark_bar(size=20).encode(
    x='發生季度',
    y='count',
    color=alt.Color('value').scale(scheme='viridis'),
    order=alt.Order('value', sort='ascending')
    )
    st.altair_chart(c, use_container_width=True)
    # st.bar_chart(chart_data, x="發生年度", y="count", color="value")

with tab1:
    # Reload data
    quarters = st.multiselect('發生季度', ['2018Q1', '2018Q2', '2018Q3', '2018Q4', '2019Q1', '2019Q2',\
                                       '2019Q3', '2019Q4', '2020Q1', '2020Q2', '2020Q3', '2020Q4',\
                                       '2021Q1', '2021Q2', '2021Q3', '2021Q4', '2022Q1', '2022Q2',\
                                       '2022Q3', '2022Q4', '2023Q1', '2023Q2', '2023Q3'], ['2022Q4'])
    dfs = pd.DataFrame()
    for quarter in quarters:
        print('load '+quarter)
        df = pd.read_parquet('./data/'+quarter[0:4]+'.parquet')
        df = df[df['發生季度']==quarter]
        df = df[(df['經度']>xmin) & (df['經度']<xmax) & (df['緯度']>ymin) & (df['緯度']<ymax)][cols].drop_duplicates().reset_index(drop=True)
        dfs = pd.concat([dfs, df])
        
    # Filter dataframe
    if (city != '全台'):
        dfs = dfs[dfs['發生地點'].str[0:3] == city]
    if (option != '全部'):
        dfs = dfs[dfs[variable] == option]
    else: 
        dfs = dfs[cols]

    # Get center lat and lon
    if (city != '全台'):
        lat = dfs[dfs['發生地點'].str.contains(city)]['緯度'].mean()
        lon = dfs[dfs['發生地點'].str.contains(city)]['經度'].mean()
        zoom = 12
    else: 
        lat = 23.5
        lon = 121
        zoom = 7

    # Plot
    basemap = xyz.Stadia.AlidadeSmoothDark
    m = leafmap.Map(center=[lat, lon], zoom=zoom)
    m.add_basemap(basemap)

    if dfs.shape[0]>0:
        print('test', dfs.shape)
        dfs['value'] = 1

        m.add_heatmap(dfs, latitude="緯度", longitude='經度', value="value", radius=20)
        m.add_points_from_xy(dfs, x="經度", y="緯度")
        m.to_streamlit(width=700, height=500, add_layer_control=True)