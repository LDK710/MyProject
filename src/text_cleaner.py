import re

def clean_text(text):
    """
    Tiền xử lý văn bản cho một trang cụ thể:
    - Loại bỏ khoảng trắng và tab thừa.
    - Xóa các dòng rỗng liên tiếp.
    - Cắt bỏ khoảng trắng ở hai đầu chuỗi.
    """
    if not isinstance(text, str):
        return ""
        
    # Thay thế 2 hoặc nhiều dấu xuống dòng liên tiếp bằng 1 dấu xuống dòng
    text = re.sub(r'\n{2,}', '\n', text)
    
    # Thay thế nhiều khoảng trắng hoặc tab liên tiếp bằng 1 khoảng trắng
    text = re.sub(r'[ \t]+', ' ', text)

    # Xóa các dòng mô tả icon do LlamaParse trích xuất (VD: "icon: purple square")
    text = re.sub(r'icon:\s*[a-zA-Z0-9 _-]+', '', text)
    
    # Xóa khoảng trắng ở đầu và cuối văn bản
    return text.strip()


def remove_empty_pages(pages):
    """
    Lọc và loại bỏ các trang rỗng hoặc chứa nội dung rác không có ý nghĩa.
    - Đầu vào: danh sách các dictionary trang [{"page": 1, "text": "..."}]
    - Điều kiện lọc: Văn bản sau khi làm sạch phải dài hơn 5 ký tự.
    """
    valid_pages = []
    
    for page in pages:
        # Làm sạch text trước khi kiểm tra để đảm bảo độ dài chính xác
        cleaned_content = clean_text(page.get('text', ''))
        
        # Bỏ qua nếu nội dung rỗng hoặc quá ngắn (ví dụ: chỉ có mỗi số trang)
        if len(cleaned_content) > 5:
            valid_pages.append({
                "page": page.get('page'),
                "text": cleaned_content
            })
            
    return valid_pages


def validate_document(pages):
    """
    Kiểm tra tính toàn vẹn của cấu trúc tài liệu sau khi trích xuất.
    - Đảm bảo tài liệu có dữ liệu.
    - Đảm bảo mỗi trang đều chứa đúng các khóa (keys) cần thiết: 'page' và 'text'.
    """
    if not pages or not isinstance(pages, list):
        return False, "Lỗi: Tài liệu rỗng hoặc sai định dạng mảng."
        
    for idx, page in enumerate(pages):
        if not isinstance(page, dict):
            return False, f"Lỗi: Phần tử tại vị trí {idx} không phải là dictionary."
            
        if 'page' not in page or 'text' not in page:
            return False, f"Lỗi: Trang thứ {idx + 1} thiếu trường 'page' hoặc 'text'."
            
    return True, f"Tài liệu hợp lệ. Tổng số trang: {len(pages)}"