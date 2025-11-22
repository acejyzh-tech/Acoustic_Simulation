import streamlit as st
import pandas as pd
import altair as alt
import JYAcoustic as ac
st.header("计权数据生成", divider=True)
freq0 = ""
for i in range(401): freq0 += str(10**(i/100+1))+"\n"
input_data = st.text_area("请输入你想要计算的频率点数据（每行一个频率值）", freq0)
input_data = input_data.replace(' ', ',')
input_data = input_data.replace('\t', ',')
indata = input_data.split('\n')
indata = [row.split(',') for row in indata]
data = []
for row in indata:
    try:
        data.append([float(num) for num in row])
    except ValueError:
        pass
N = len(data)
st.caption(f"有效数据长度：{N}")
freq = [row[0] for row in data]
values = [ac.A_weight(num) for num in freq]  # 计算计权值
if len(data[0])==1:
    df = pd.DataFrame({'频率': freq, 'A计权值': values})
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('频率:Q', title='频率 (Hz)', scale=alt.Scale(type='log')),
        y=alt.Y('A计权值:Q', title='A计权值 (dB)'),
        tooltip=['频率:Q', 'A计权值:Q']
        ).properties(title='计权值数据')
    
else:
    lin = [row[1] for row in data]
    weighted = [lin[i]+values[i] for i in range(len(lin))]
    df = pd.DataFrame({'频率': freq, '未计权': lin,  '计权后': weighted})
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('频率:Q', title='频率 (Hz)', scale=alt.Scale(type='log')),
        y=alt.Y('未计权:Q', title='未计权 (dB)')
    ).properties(title='计权值数据')
    chart += alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('频率:Q', title='频率 (Hz)', scale=alt.Scale(type='log')),
        y=alt.Y('计权后:Q', title='计权后 (dB)')
    ).properties(title='计权值数据')
st.altair_chart(chart, use_container_width=True)
