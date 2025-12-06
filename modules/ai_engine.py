# modules/ai_engine.py
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
    智能挑選模型函數：
    不要硬編碼名字，而是從 Google 返回的真實列表中，
    挑選出最強、最新的一個。
    """
    try:
        # 1. 獲取所有可用模型
        all_models = list(genai.list_models())
        
        # 2. 過濾出支持內容生成的模型 (排除掉 embedding 那些)
        valid_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        if not valid_models:
            return None, "沒有找到支持生成的模型"

        # 3. 定義優先級 (越靠前越優先)
        # 我們優先找 1.5 Pro，其次是 Flash，最後是普通 Pro
        # 這裡的 * 是通配符，可以匹配 models/gemini-1.5-pro-001 等任何變體
        priorities = [
            "*gemini-1.5-pro*",       # 第一志願：任何版本的 1.5 Pro
            "*gemini-1.5-flash*",     # 第二志願：任何版本的 1.5 Flash
            "*gemini-pro*",           # 第三志願：老版 Pro
            "*gemini*"                # 保底：隨便來個 Gemini 相關的
        ]
        
        # 4. 按優先級遍歷匹配
        for pattern in priorities:
            for model_name in valid_models:
                if fnmatch.fnmatch(model_name, pattern):
                    return model_name, None # 找到了！直接返回真實名字
        
        # 5. 如果上面都沒匹配到，就默認拿列表裡的第一個
        return valid_models[0], None

    except Exception as e:
        return None, str(e)

def generate_ppt_content(topic, uploaded_files):
    # 1. 配置
    if not configure_gemini():
        return "配置錯誤，無法生成。"
    
    # 2. 動態獲取模型名字 (這是解決 404 的核心！)
    model_name, error = get_best_available_model()
    
    if not model_name:
        return f"無法自動找到可用模型。錯誤信息: {error}"
    
    # 3. 開始生成
    try:
        # 構建 Prompt
        prompt = f"""
        你的身份：清華大學入學考試語文輔導專家。
        任務：閱讀提供的教材資料，為主題「{topic}」製作一份講課用的幻燈片代碼。
        工具：Marp (Markdown Presentation)。
        
        要求：
        1. **排版**：必須包含 Marp 標頭 (theme: gaia)。
        2. **結構**：封面、目錄、核心知識點提取、易錯點辨析、真題演練、總結。
        3. **輸出**：僅輸出 Markdown 源代碼。
        """
        
        content_parts = [prompt]
        
        # 處理文件
        if uploaded_files:
            for file in uploaded_files:
                content_parts.append({
                    "mime_type": file.type,
                    "data": file.getvalue()
                })
        
        # 實例化模型 (使用剛才動態找到的那個名字)
        model = genai.GenerativeModel(model_name)
        
        # 發送請求
        response = model.generate_content(content_parts)
        
        # 在結果前面加上這行註釋，讓你看到到底用了哪個模型
        header_info = f"<!-- ✅ 成功！本次生成使用的是: {model_name} -->\n"
        return header_info + response.text

    except Exception as e:
        return f"生成失敗。\n嘗試使用的模型: {model_name}\n錯誤信息: {str(e)}"
