from src.config import DATA_DIR
from src.pdf_loader import extract_pdf
from src.text_cleaner import remove_empty_pages, validate_document
from src.file_handler import save_json, load_json

def main():
    print("=== CHƯƠNG TRÌNH TRÍCH XUẤT VÀ LÀM SẠCH PDF SANG JSON ===")
    
    # 1. Đường dẫn file PDF và file JSON đích
    pdf_path = DATA_DIR / "Buoi_1_AI_Engineering_2026.pptx.pdf"
    cleaned_json_path = DATA_DIR / "ketqua_pdf_cleaned.json"

    # 2. Gọi hàm đọc PDF
    print(f"\n[Bước 1] Đang xử lý file: {pdf_path.name}...")
    extracted_pages = extract_pdf(pdf_path)

    # 3. Xử lý dữ liệu nếu đọc thành công
    if extracted_pages:
        print(f"-> Đã trích xuất thành công {len(extracted_pages)} trang thô.")
        
        # 4. Kiểm tra định dạng dữ liệu trích xuất
        print(f"\n[Bước 2] Kiểm tra định dạng dữ liệu trích xuất...")
        is_valid, validation_msg = validate_document(extracted_pages)
        print(f"- {validation_msg}")
        
        if is_valid:
            # 5. Làm sạch văn bản và loại bỏ trang rỗng
            print(f"\n[Bước 3] Làm sạch văn bản và loại bỏ trang rỗng...")
            cleaned_pages = remove_empty_pages(extracted_pages)
            
            # Đóng gói kết quả vào Dictionary sau khi đã làm sạch
            cleaned_payload = {
                "source_file": pdf_path.name,
                "total_pages": len(cleaned_pages),
                "pages": cleaned_pages
            }
            
            # 6. Lưu xuống ổ cứng thành file JSON
            print(f"\n[Bước 4] Đang lưu dữ liệu hoàn chỉnh sang {cleaned_json_path.name}...")
            save_json(cleaned_payload, cleaned_json_path)
            print(f"-> Hoàn tất! Đã lưu {len(cleaned_pages)} trang hợp lệ sau khi lọc.")

            # 7. Đọc ngược lại từ JSON đã làm sạch lên để nghiệm thu
            print(f"\n[Bước 5] Mở file {cleaned_json_path.name} để kiểm tra...")
            verified_data = load_json(cleaned_json_path)
            
            if verified_data and verified_data['pages']:
                print(f"- Tên tài liệu: {verified_data['source_file']}")
                print(f"- Tổng số trang: {verified_data['total_pages']}")
                # Trích xuất thử 150 ký tự đầu tiên của trang hợp lệ đầu tiên để xem trước
                trang_1_preview = verified_data['pages'][0]['text'][:150]
                print(f"- Bản xem trước trang đầu tiên: {trang_1_preview}...\n")
        else:
            print("-> Dừng tiền xử lý do tài liệu đầu vào không hợp lệ.")

    else:
        print(f"-> [Thất bại] Vui lòng chép file '{pdf_path.name}' vào thư mục 'data/'.")

if __name__ == "__main__":
    main()