# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any

import numpy as np

import streamlit as st
import pandas as pd



def animation_demo() -> None:
    # Interactive Streamlit elements, like these sliders, return their value.
    # This gives you an extremely simple interaction model.
    

st.set_page_config(page_title="Animation demo", page_icon=":material/animation:")
st.title("Animation demo")
st.write(
    """
    This app shows how you can use Streamlit to build cool animations.
    It displays an animated fractal based on the Julia Set. Use the slider
    to tune different parameters.
    """
)



# 设置页面标题（中文）
st.title("DataFrame 单选交互示例")

# 创建示例数据
data = {
    "姓名": ["张三", "李四", "王五", "赵六"],
    "年龄": [28, 32, 25, 30],
    "城市": ["北京", "上海", "广州", "深圳"]
}
df = pd.DataFrame(data)

# 初始化会话状态
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = None

# 自定义行样式函数
def highlight_row(row):
    return ['background-color: yellow' if i == st.session_state.selected_index else '' for i in range(len(df))]

# 显示数据编辑器
edited_df = st.data_editor(
    df,
    hide_index=True,
    column_config={
        "选择": st.column_config.CheckboxColumn("选择", help="点击选择该行"),
    },
    on_change=lambda: st.session_state.update(
        selected_index=edited_df.index[edited_df['选择']].iloc[0] if not edited_df['选择'].isna().all() else None
    ),
    kwargs={"use_container_width": True}
)

# 显示选中行数据
if st.session_state.selected_index is not None:
    selected_row = df.iloc[st.session_state.selected_index]
    st.success("您选中了以下数据：")
    st.dataframe(
        selected_row.to_frame().T,
        hide_index=True,
        use_container_width=True,
        column_config={
            "姓名": st.column_config.TextColumn("姓名"),
            "年龄": st.column_config.NumberColumn("年龄"),
            "城市": st.column_config.TextColumn("城市")
        }
    )
else:
    st.info("请从表格中选择一行进行查看")

# animation_demo()
