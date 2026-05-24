import fitz  # PyMuPDF
import os

def draw_highlight_on_pdf(pdf_path, target_component): # ลบตัวแปร page_num ทิ้งไปเลย
    doc = fitz.open(pdf_path)
    
    target_bbox = None
    found_page = None
    page_number = 0
    
    # วนลูปค้นหาทุกหน้าในไฟล์ PDF
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        words = page.get_text("words") 
        
        for word in words:
            x0, y0, x1, y1, text = word[:5]
            if text == target_component:
                target_bbox = fitz.Rect(x0, y0, x1, y1)
                found_page = page
                page_number = page_index + 1 # เก็บเลขหน้าไว้บอกช่าง (บวก 1 เพราะ index เริ่มที่ 0)
                break
        
        if target_bbox:
            break # ถ้าเจอแล้ว ให้หยุดค้นหาหน้าต่อไปทันที
            
    # ถ้าระบุพิกัดได้ ให้วาดกรอบสีแดง
    if target_bbox and found_page:
        target_bbox = target_bbox + (-3, -3, 3, 3)
        found_page.draw_rect(target_bbox, color=(1, 0, 0), width=1.5)
        
        zoom_matrix = fitz.Matrix(2.0, 2.0)
        pix = found_page.get_pixmap(matrix=zoom_matrix)
        
        # เซฟชื่อไฟล์แบบมีเลขหน้ากำกับด้วย
        output_filename = f"highlighted_{target_component}_page{page_number}.png"
        output_path = os.path.abspath(output_filename)
        pix.save(output_path)
        
        # คืนค่ากลับไป 2 อย่าง: [ที่อยู่ไฟล์รูปภาพ, เลขหน้าที่เจอ]
        return output_path, page_number 
    else:
        return None, None