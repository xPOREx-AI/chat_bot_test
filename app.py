import streamlit as st
import re
import os
import networkx as nx
from google import genai # เปลี่ยนมาใช้ Gemini API

from draw_highlight import draw_highlight_on_pdf
from circuit_tracer import build_circuit_graph

# ดึง API Key จากระบบหลังบ้านของ Streamlit
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
llm_model = genai.GenerativeModel('gemini-3.5-flash') # ใช้โมเดลตัวเบาและเร็ว

def extract_intent(user_message):
    prompt = f"""
    คุณคือ AI ผู้ช่วยวิศวกร หน้าที่ของคุณคือสกัด 'รหัสอุปกรณ์' (Component ID) จากข้อความ
    รหัสอุปกรณ์มักจะขึ้นต้นด้วยเครื่องหมาย '-' เช่น -QAB1, -FA1, -PFV1
    ตอบกลับมาแค่รหัสอุปกรณ์เท่านั้น ห้ามพิมพ์อย่างอื่น
    
    ข้อความจากช่าง: "{user_message}"
    """
    
    try:
        response = llm_model.generate_content(prompt)
        extracted_text = response.text.strip()
        match = re.search(r'-[A-Z0-9]+', extracted_text)
        return match.group(0) if match else None
    except Exception as e:
        print(f"API Error: {e}")
        return None

# --- ส่วนของการสร้างหน้า Web UI ด้วย Streamlit ---

st.set_page_config(page_title="AI Maintenance", page_icon="🤖")
st.title("🤖 AI Maintenance Assistant")
st.markdown("ระบบช่วยช่างเทคนิคไล่วงจรไฟฟ้าและค้นหาตำแหน่งอุปกรณ์")

# สร้างตัวแปรเก็บประวัติการแชท (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงผลประวัติการแชททั้งหมด
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # ถ้ามีไฟล์รูปภาพแนบมาด้วย ให้แสดงรูป
        if "image" in msg and msg["image"] is not None:
            st.image(msg["image"])

# รับข้อความจากผู้ใช้
if prompt := st.chat_input("พิมพ์อาการเสีย หรือรหัสอุปกรณ์ที่นี่ (เช่น เบรกเกอร์ -QAB1 ทริป)..."):
    
    # แสดงข้อความผู้ใช้บนจอ และเก็บลงประวัติ
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ให้ AI เริ่มทำงาน
    with st.chat_message("assistant"):
        with st.spinner("🤖 กำลังวิเคราะห์ข้อมูลและไล่วงจร..."): # แสดงโหลดดิ้งหมุนๆ
            
            target_id = extract_intent(prompt)
            
            if target_id:
                reply_text = f"✅ พบรหัสอุปกรณ์: **{target_id}**\n\n"
                
                # ไล่วงจร Graph DB
                G = build_circuit_graph()
                if G.has_node(target_id):
                    downstream = list(nx.descendants(G, target_id))
                    if downstream:
                        reply_text += "⚠️ **อุปกรณ์ที่ได้รับผลกระทบหากจุดนี้เสีย:**\n"
                        for node in downstream:
                            reply_text += f"- {node} ({G.nodes[node].get('type')})\n"
                
                st.markdown(reply_text)
                
                # วาดรูปลงบน PDF
                pdf_file = "Mock_Mechanics.pdf" 
                try:
                    img_path, found_page_num = draw_highlight_on_pdf(pdf_file, target_id) 
                    
                    if img_path and os.path.exists(img_path):
                        success_msg = f"👇 นี่คือตำแหน่งบนแบบไฟฟ้า (พบที่หน้า {found_page_num}) ครับ:"
                        st.markdown(success_msg)
                        st.image(img_path) # คำสั่งแสดงรูปของ Streamlit (ง่ายๆ แบบนี้เลย!)
                        
                        # เก็บข้อความและรูปภาพลงประวัติแชทของบอท
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": reply_text + "\n\n" + success_msg,
                            "image": img_path
                        })
                    else:
                        error_msg = f"❌ ค้นหาทั่วทั้งเล่มแล้ว ไม่พบรหัสอุปกรณ์ '{target_id}' ในแบบไฟฟ้า"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": reply_text + "\n\n" + error_msg})
                        
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาดในการวาดรูป: {str(e)}")
            else:
                not_found_msg = "❌ ขออภัยครับ ผมไม่พบรหัสอุปกรณ์ในข้อความของคุณ ช่วยระบุรหัส (เช่น -QAB1) ให้ชัดเจนอีกครั้งครับ"
                st.markdown(not_found_msg)
                st.session_state.messages.append({"role": "assistant", "content": not_found_msg})
