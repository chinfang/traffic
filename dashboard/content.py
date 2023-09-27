import streamlit as st
import altair as alt
import pandas as pd
import xyzservices.providers as xyz
import leafmap

def config():
    # Set streamlit
    st.set_page_config(
        page_title='台灣交通熱點地圖',
        page_icon='🔥',
        layout='wide')
    
    # Hide footer
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    
def map(xmin, xmax, ymin, ymax, quarters, city, option, variable):
    array_cols = ['當事者事故發生時年齡', '肇因研判大類別名稱-主要', '肇因研判子類別名稱-主要']
    dfs = pd.DataFrame()
    for quarter in quarters:
        print('load '+quarter)
        df = pd.read_parquet('./data/'+quarter[0:4]+'.parquet')
        df = df[df['發生季度']==quarter]
        df = df[(df['經度']>xmin) & (df['經度']<xmax) & (df['緯度']>ymin) & (df['緯度']<ymax)]#.drop_duplicates()
        dfs = pd.concat([dfs, df])
    
    # Filter dataframe
    if (city != '全台'):
        dfs = dfs[dfs['發生地點'].str[0:3] == city]
    if (option != '全部'):
        if variable in array_cols:
            dfs = dfs[dfs[variable].apply(lambda x: '13-17' in x)]
        else:
            dfs = dfs[dfs[variable] == option]
    else: 
        dfs = dfs#[cols]
    dfs = dfs.reset_index(drop=True)

    # Get center lat and lon
    if (city != '全台'):
        lat = dfs[dfs['發生地點'].str.contains(city)]['緯度'].mean()
        lon = dfs[dfs['發生地點'].str.contains(city)]['經度'].mean()
        zoom = 12
    else: 
        lat = 23.5
        lon = 121
        zoom = 7

    return dfs, lat, lon, zoom

def stats(city, variable):
    country = st.checkbox('全台')
    df_stats = pd.read_parquet('./data/stats.parquet')
    
    if country:
        chart_data = df_stats[(df_stats['因子']==variable)].reset_index(drop=True)
    else:
        chart_data = df_stats[(df_stats['因子']==variable) & (df_stats['發生縣市']==city)].reset_index(drop=True)
    c = alt.Chart(chart_data).mark_bar(size=20).encode(
    x='發生季度',
    y='count',
    color=alt.Color('value').scale(scheme='viridis'),
    order=alt.Order('value', sort='ascending')
    )
    st.altair_chart(c, use_container_width=True)

def info():
    st.markdown('台灣交通熱點地圖呈現A1類及A2類交通事故之視覺化以及相關統計資料，希望能提供肇因研判以外的分析，  \n\
                 以增進道路和號誌設計的系統化解決方案。')
    for i in range(20):
        st.markdown('\n\n')
    st.markdown('資料來源: [kiang\'s github](https://github.com/kiang/NPA_TMA) ，源頭為[政府開放資料平台](https://data.gov.tw/dataset/12197)  \n'
                'Note: 2018-2022年資料包含A1和A2類交通事故，2023年目前只包含A1事故  \n'
                '<a href="mailto:chinfang.lin.g@gmail.com">Contact</a>', unsafe_allow_html=True)