# modules/ai_engine.py
import google.generativeai as genai
import streamlit as st
import os

# ==========================================
# 🚑 網絡急救包 (如果你依然遇到 404 報錯)
# ==========================================
# 如果你的 VPN 端口是 7890，請將下面兩行的 # 號去掉
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

def configure_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Gemini 配置失敗: {e}")
        return False

def generate_ppt_content(topic, uploaded_files):
    """
    :param topic: 課程主題
    :param uploaded_files: 一個包含多個文件的列表 (可以是 Image 或 PDF)
    """
    if not configure_gemini():
        return "配置錯誤，無法生成。"
    
    # 這裡我們顯式指定最新版本，防止 404
    model_name = "gemini-1.5-pro-latest" 
    
    try:
        model = genai.GenerativeModel(model_name)
    except Exception:
        # 如果 latest 也不行，嘗試最原始的名稱
        model = genai.GenerativeModel("gemini-1.5-pro")
    
    # 構建 Prompt
    prompt = f"""
    你的身份：清華大學入學考試語文輔導專家。
    任務：閱讀提供的教材資料（圖片或PDF），為主題「{topic}」製作一份講課用的幻燈片代碼。
    工具：Marp (Markdown Presentation)。
    
    要求：
    1. **排版**：
       - 必須包含 Marp 標頭 (theme: gaia)。
    2. **結構**：
       - 封面、目錄。
       - **核心知識點**：請仔細閱讀上傳的資料，將里面的重點提取出來做成 PPT。
       - **易錯點辨析**：結合清華考試特點進行補充。
       - 真題/例題演練。
       - 課堂總結。
    3. **輸出**：僅輸出 Markdown 源代碼。
    """
    
    # 構建發送給 Gemini 的內容列表
    content_parts = [prompt]
    
    # 循環處理每一個上傳的文件
    if uploaded_files:
        for file in uploaded_files:
            # 獲取文件類型 (MIME type)
            mime_type = file.type
            file_data = file.getvalue()
            
            # Gemini 支持 image/jpeg, image/png, application/pdf
            content_parts.append({
                "mime_type": mime_type,
                "data": file_data
            })
        
    with st.spinner(f"正在閱讀 {len(uploaded_files)} 份教材資料並構建講義 (Gemini 1.5 Pro)..."):
        try:
            # 發送請求
            response = model.generate_content(content_parts)
            return response.text
        except Exception as e:
            # 這裡會打印出更詳細的錯誤信息幫助調試
            return f"生成失敗 (Error): {str(e)}"