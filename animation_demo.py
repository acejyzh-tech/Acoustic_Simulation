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


# 示例数字
number = 123456

# 使用 HTML + JavaScript 实现复制功能
st.markdown(
    f"""
    <script>
    function copyToClipboard(text) {{
        navigator.clipboard.writeText(text).then(function() {{
            alert('已复制到剪贴板: ' + text);
        }}, function(err) {{
            alert('复制失败: ' + err);
        }});
    }}
    </script>
    <div style="cursor: pointer; display: inline-block; padding: 8px; background: #f0f0f0; border-radius: 4px;" 
         onclick="copyToClipboard('{number}')">
        {number}
    </div>
    """,
    unsafe_allow_html=True
)
