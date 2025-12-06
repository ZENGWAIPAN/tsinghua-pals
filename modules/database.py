# modules/database.py
import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone

# 1. 初始化連接
# 使用 @st.cache_resource 確保不會每次刷新頁面都重新連接數據庫，提高速度
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# 2. 新增知識點 (當你生成 PPT 時調用)
def add_knowledge_point(subject, topic, content):
    """
    將新學的知識點存入數據庫
    :param subject: 科目 (如：文言文)
    :param topic: 主題 (如：虛詞'之')
    :param content: 核心筆記內容
    """
    data = {
        "subject": subject,
        "topic": topic,
        "content": content,
        "mastery_level": 0,  # 初始等級為 0
        "last_review_date": datetime.now(timezone.utc).isoformat(),
        "next_review_date": datetime.now(timezone.utc).isoformat() # 默認今天就需要複習
    }
    try:
        # 執行插入操作
        response = supabase.table("knowledge_points").insert(data).execute()
        return True, "保存成功！"
    except Exception as e:
        return False, f"保存失敗: {str(e)}"

# 3. 獲取需要複習的知識點 (生成測驗時調用)
def get_points_to_review():
    """
    獲取所有需要複習的知識點（目前簡單邏輯：獲取所有）
    未來我們會在這裡加入艾賓浩斯算法
    """
    try:
        # 查詢所有數據，按創建時間倒序排列
        response = supabase.table("knowledge_points").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"讀取數據失敗: {e}")
        return []

# 4. 更新掌握程度 (測驗結束後調用)
def update_mastery(point_id, new_level):
    try:
        supabase.table("knowledge_points").update({"mastery_level": new_level}).eq("id", point_id).execute()
        return True
    except Exception as e:
        return False