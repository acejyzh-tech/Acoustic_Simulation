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
##########################
# Developed by J.Y.Zhang #
##########################

import streamlit as st
from pathlib import Path

dir_path = Path(__file__).parent

def run() -> None:
    page = st.navigation(
        {
            "JYZhang 的声学工具箱": [

                st.Page(
                    dir_path / "page_weighting.py",
                    title="计算A计权值",
                    icon="A",
                ),
                st.Page(
                    dir_path / "page_fr_simulation.py",
                    title="麦克风集中参数法仿真",
                    icon=":material/show_chart:",
                ),
                st.Page(
                    dir_path / "animation_demo.py",
                    title="由低衰和谐振峰点生成麦克风频响曲线",
                    icon=":material/show_chart:",
                ),
            ]
        }
    )
    page.run()

if __name__ == "__main__":
    run()
