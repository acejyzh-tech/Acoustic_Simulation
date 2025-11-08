import streamlit as st
import pandas as pd
import altair as alt
import JYAcoustic as ac

freq0 = ""
for i in range(401): freq0 += str(10**(i/100+1))+"\n"
input_data = st.text_area("请输入你想要计算的频率点数据（每行一个频率值）", freq0)

if st.button("计算计权值"):
    try:
        freq = [float(line.strip()) for line in input_data.splitlines() if line.strip()]
        values = [ac.A_weight(num) for num in freq]  # 计算计权值
        
        df = pd.DataFrame({'频率': freq, 'A计权值': values})
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('频率:Q', title='频率 (Hz)', scale=alt.Scale(type='log')),
            y=alt.Y('A计权值:Q', title='A计权值 (dB)'),
            tooltip=['频率:Q', 'A计权值:Q']
        ).properties(title='计权值数据')
        st.altair_chart(chart, use_container_width=True)
    
    except ValueError:
        st.error("请输入有效的数值！")
