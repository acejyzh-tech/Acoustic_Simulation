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


# 初始化 session_state
if 'selected_row' not in st.session_state:
    st.session_state['selected_row'] = None
if 'data_editor' not in st.session_state:
    st.session_state['data_editor'] = pd.DataFrame({
        '名称': ['项目A', '项目B', '项目C'],
        '数量': [10, 20, 30],
        '选择': [False, False, False]
    })

# 定义列配置
column_config = {
    '名称': st.column_config.TextColumn("名称", help="项目名称"),
    '数量': st.column_config.NumberColumn("数量", help="项目数量"),
    '选择': st.column_config.CheckboxColumn("选择", help="选择此行")
}

# 回调函数处理选中逻辑
def handle_selection():
    # 获取当前数据框
    updated_df = st.session_state['data_editor'].copy()
    # 找到所有选中的行
    selected_rows = updated_df[updated_df['选择']]
    if not selected_rows.empty:
        # 如果有多个选中行，只保留最后一个
        if len(selected_rows) > 1:
            # 将其他行的“选择”设为False
            updated_df.loc[updated_df.index != selected_rows.index[-1], '选择'] = False
        # 更新 session_state 中的选中行
        st.session_state['selected_row'] = selected_rows.index[-1]
    else:
        st.session_state['selected_row'] = None
    # 更新 session_state 中的数据框
    st.session_state['data_editor'] = updated_df

# 显示 data_editor
st.write("### 使用 data_editor 的单选表格")
df_editor = st.data_editor(
    st.session_state['data_editor'],
    column_config=column_config,
    on_change=handle_selection,
    key="data_editor"
)

# 显示选中的行信息
if st.session_state['selected_row'] is not None:
    st.success("当前选中行：")
    st.dataframe(st.session_state['data_editor'].iloc[st.session_state['selected_row']].to_frame().T)
else:
    st.info("请选择一行")
