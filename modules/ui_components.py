# modules/ui_components.py
import streamlit as st

def apply_tsinghua_theme():
    """
    注入清華紫 CSS 樣式
    """
    # 清華紫 Hex: #660874
    st.markdown("""
        <style>
        /* 全局背景微調 */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* 標題樣式 - 清華紫 + 襯線體 */
        h1, h2, h3 {
            color: #660874 !important;
            font-family: 'Source Han Serif SC', 'Songti SC', serif; 
        }
        
        /* 按鈕樣式 */
        div.stButton > button {
            background-color: #660874;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }
        div.stButton > button:hover {
            background-color: #8c2f9d;
            color: white;
            border-color: #8c2f9d;
            transform: scale(1.02);
        }
        
        /* 輸入框聚焦顏色 */
        div[data-baseweb="input"] > div {
            border-color: #660874;
        }
        
        /* 側邊欄優化 */
        section[data-testid="stSidebar"] {
            background-color: #f3eef5; /* 極淡的紫色背景 */
        }
        </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle):
    """
    渲染帶有裝飾線的標題組件
    """
    st.markdown(f"""
    <div style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid #660874; margin-bottom: 30px;">
        <h1 style="margin-bottom: 10px;">🏛️ {title}</h1>
        <p style="color: #666; font-style: italic; font-size: 1.1em;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)