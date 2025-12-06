import google.generativeai as genai
import streamlit as st
import fnmatch

def configure_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Gemini 配置失敗: {e}")
        return False

def get_best_available_model():
    """
    智能挑選模型：避免 404 的核心邏輯
    """
    try:
        all_models = list(genai.list_models())
        valid_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        if not valid_models:
            return None, "沒有找到支持生成的模型"

        # 優先級策略
        priorities = [
            "*gemini-1.5-pro*", 
            "*gemini-1.5-flash*", 
            "*gemini-pro*", 
            "*gemini*"
        ]
        
        for pattern in priorities:
            for model_name in valid_models:
                if fnmatch.fnmatch(model_name, pattern):
                    return model_name, None
        
        return valid_models[0], None

    except Exception as e:
        return None, str(e)

def generate_ppt_content(topic, uploaded_files):
    # 1. 配置與選模型
    if not configure_gemini():
        return "配置錯誤，無法生成。"
    
    model_name, error = get_best_available_model()
    if not model_name:
        return f"無法自動找到可用模型。錯誤信息: {error}"
    
    # 2. 構建 Prompt (含 CSS 排版優化)
    prompt = f"""
    你的身份：清華大學入學考試語文輔導專家。
    任務：閱讀提供的教材資料，為主題「{topic}」製作一份講課用的幻燈片代碼。
    工具：Marp (Markdown Presentation)。
    
    【核心排版規則 (至關重要)】：
    1. **防止爆版**：Marp 默認字號很大。如果一張幻燈片內容超過 6 行，或者包含表格，**必須**使用 CSS 縮小字號，或者拆分成兩張幻燈片。
    2. **強制 CSS 樣式**：
       - 請在文檔開頭準確輸出以下樣式塊，不要修改：
       <style>
       section {{
           font-size: 24px;
           padding: 40px;
       }}
       h1, h2 {{
           font-size: 1.5em;
           color: #660874;
       }}
       table {{
           font-size: 20px;
       }}
       </style>
    3. **表格處理**：如果表格行數超過 6 行，必須拆分為兩個表格，放在兩頁幻燈片上。
    
    【內容結構要求】：
    1. **Marp 標頭**：
       ---
       marp: true
       theme: gaia
       class: lead
       ---
    2. **封面**：標題、副標題。
    3. **目錄**。
    4. **核心內容**：(知識點需詳細，但請遵循上述排版規則)。
    5. **易錯點辨析**：(重點)。
    6. **真題演練**。
    7. **總結**。
    
    **輸出**：僅輸出 Markdown 源代碼，不要包含 ```markdown 標記。
    """
    
    content_parts = [prompt]
    
    # 3. 處理文件
    if uploaded_files:
        for file in uploaded_files:
            content_parts.append({
                "mime_type": file.type,
                "data": file.getvalue()
            })
    
    # 4. 發送請求
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(content_parts)
        
        header_info = f"<!-- ✅ 排版優化模式 | 模型: {model_name} -->\n"
        return header_info + response.text

    except Exception as e:
        return f"生成失敗。\n嘗試使用的模型: {model_name}\n錯誤信息: {str(e)}"
