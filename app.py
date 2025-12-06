import streamlit as st
from modules.ui_components import apply_tsinghua_theme, render_header
from modules.ai_engine import generate_ppt_content
from modules.database import add_knowledge_point

st.set_page_config(page_title="清華衝刺 PALS", layout="wide", page_icon="🏛️")
apply_tsinghua_theme()

st.sidebar.title("🏛️ PALS 導航")
menu = st.sidebar.radio("選擇功能", ["📚 智能備課 (PPT)", "📝 今日小測 (開發中)", "📊 進度看板 (開發中)"])

if menu == "📚 智能備課 (PPT)":
    render_header("智能備課系統", "支持多圖、PDF 上傳，一鍵生成清華級別講義")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.info("💡 步驟 1：上傳教材資料 (支持多選)")
        # 修改點：accept_multiple_files=True, type 增加了 pdf
        uploaded_files = st.file_uploader(
            "支持 JPG, PNG, PDF (可同時上傳多個文件)", 
            type=['jpg', 'png', 'jpeg', 'pdf'], 
            accept_multiple_files=True
        )
        
        st.info("💡 步驟 2：定義本節課主題")
        topic = st.text_input("主題名稱", placeholder="例如：古詩十九首賞析")

        generate_btn = st.button("🚀 開始生成講義", use_container_width=True)

    if generate_btn:
        if not topic:
            st.error("請輸入主題名稱！")
        elif not uploaded_files:
            st.error("請至少上傳一份資料（圖片或 PDF）！")
        else:
            # 直接把 uploaded_files 列表傳給 AI 模塊
            ppt_code = generate_ppt_content(topic, uploaded_files)
            
            st.session_state['generated_ppt'] = ppt_code
            st.session_state['current_topic'] = topic

    with col2:
        if 'generated_ppt' in st.session_state:
            result = st.session_state['generated_ppt']
            
            # 檢查結果是不是報錯信息
            if result.startswith("生成失敗"):
                st.error(result)
                st.markdown("### 🚑 排錯指南")
                st.markdown("如果顯示 404，請嘗試打開 `modules/ai_engine.py`，取消第 9, 10 行的註釋，填入你的 VPN 端口。")
            else:
                st.success("✅ 講義生成完畢！")
                st.text_area("Marp Markdown 代碼", result, height=400)
                
                st.info("💡 複製代碼到 VS Code 即可查看 PPT")

                if st.button("💾 保存到知識庫"):
                    success, msg = add_knowledge_point(
                        subject="語文", 
                        topic=st.session_state['current_topic'], 
                        content=result
                    )
                    if success:
                        st.toast("已存入數據庫！", icon="🎉")
                    else:

                        st.error(msg)

# ... (前面的代碼保持不變) ...

# ==========================================
# 🚑 系統診斷模式 (添加到代碼最後)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🔧 系統診斷")

if st.sidebar.checkbox("開啟診斷面板"):
    st.title("🏥 系統體檢報告")
    
    # 1. 檢查 Key 是否存在 (只顯示前4位，防止洩露)
    try:
        key = st.secrets["GEMINI_API_KEY"]
        st.write(f"🔑 **API Key 狀態:** 已讀取 (前綴: `{key[:5]}...`)")
    except Exception as e:
        st.error(f"🔑 **API Key 狀態:** 讀取失敗! ({e})")
    
    # 2. 檢查 Google 服務器連通性 & 模型列表
    import google.generativeai as genai
    st.write("📡 **正在連接 Google 服務器...**")
    
    try:
        # 強制配置
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # 嘗試列出所有可用模型
        models = list(genai.list_models())
        model_names = [m.name for m in models]
        
        if model_names:
            st.success(f"✅ **連接成功！** 發現 {len(model_names)} 個模型。")
            st.json(model_names) # 打印出來看看有沒有 gemini-1.5-pro
        else:
            st.warning("⚠️ 連接成功，但沒有發現可用模型 (可能權限不足)。")
            
    except Exception as e:
        st.error(f"❌ **連接失敗 (致命錯誤):** {e}")
        st.info("💡 如果這裡是 404，說明你的 API Key 無效，或者 Key 所在的項目沒有開啟權限。")
