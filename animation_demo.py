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


import streamlit as st
import pandas as pd

# 初始化 session_state
if 'selected_row' not in st.session_state:
    st.session_state['selected_row'] = None

# 示例数据
data = {
    '名称': ['项目A', '项目B', '项目C'],
    '数量': [10, 20, 30]
}
df = pd.DataFrame(data)

# 显示表格
st.write("### 交互式表格（单选框）")

# 遍历每一行，生成单选框
for index, row in df.iterrows():
    # 检查当前行是否被选中
    is_selected = (index == st.session_state['selected_row'])
    
    # 创建单选框
    selected = st.checkbox(f"选择 {row['名称']}", key=index, value=is_selected)
    
    # 处理选中逻辑
    if selected:
        # 如果当前行被选中，更新 session_state
        st.session_state['selected_row'] = index
    elif is_selected:
        # 如果之前选中，现在取消
        st.session_state['selected_row'] = None

# 显示选中的行信息
if st.session_state['selected_row'] is not None:
    st.success("当前选中行：")
    st.dataframe(df.iloc[st.session_state['selected_row']].to_frame().T)
else:
    st.info("请选择一行")



# animation_demo()
