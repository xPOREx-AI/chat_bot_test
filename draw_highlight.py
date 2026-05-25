import pdfplumber
import os

def draw_highlight_on_pdf(pdf_path, target_component):
    # เปิดไฟล์ PDF 
    with pdfplumber.open(pdf_path) as pdf:
        # วนลูปค้นหาทุกหน้า
        for page_index, page in enumerate(pdf.pages):
            
            # ดึงคำและพิกัดทั้งหมดในหน้านั้นออกมา
            words = page.extract_words()
            target_word = None
            
            for word in words:
                if word['text'] == target_component:
                    target_word = word
                    break
            
            # ถ้าเจอคำเป้าหมาย
            if target_word:
                page_number = page_index + 1
                
                # เรนเดอร์หน้านั้นออกมาเป็นรูปภาพ (กำหนด Resolution = 144 เพื่อให้ภาพชัดขึ้น 2 เท่า)
                im = page.to_image(resolution=144)
                
                # กำหนดพิกัดตีกรอบ (x0, top, x1, bottom) พร้อมขยาย Padding นิดหน่อย
                bbox = (
                    target_word['x0'] - 3, 
                    target_word['top'] - 3, 
                    target_word['x1'] + 3, 
                    target_word['bottom'] + 3
                )
                
                # วาดกรอบสีแดง ความหนาเส้น 2
                im.draw_rect(bbox, stroke="red", stroke_width=2, fill=None)
                
                # บันทึกเป็นไฟล์ PNG
                output_filename = f"highlighted_{target_component}_page{page_number}.png"
                output_path = os.path.abspath(output_filename)
                im.save(output_path, format="PNG")
                
                return output_path, page_number
                
    # ถ้าหาจนจบเล่มแล้วไม่เจอ
    return None, None

# (ทดสอบรันไฟล์นี้ตรงๆ ได้ ถ้าต้องการ)
if __name__ == "__main__":
    test_pdf = "Mock_Mechanics.pdf"
    test_target = "-QAB1"
    result_path, page_num = draw_highlight_on_pdf(test_pdf, test_target)
    if result_path:
        print(f"✅ เจออุปกรณ์ที่หน้า {page_num} บันทึกไฟล์ที่: {result_path}")
    else:
        print("❌ ไม่พบอุปกรณ์")
