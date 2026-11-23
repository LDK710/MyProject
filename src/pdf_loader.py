import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def extract_pdf(pdf_path):
    """
    Trích xuất PDF sử dụng LlamaParse v2 API trực tiếp qua HTTP.
    """
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("Lỗi: Không tìm thấy LLAMA_CLOUD_API_KEY trong file .env!")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    base_url = "https://api.cloud.llamaindex.ai/api/v2/parse"

    try:
        # 1. Tải file lên kèm trường configuration bắt buộc của v2 API
        config_payload = {
            "tier": "cost_effective",
            "version": "latest"
        }
        
        with open(pdf_path, "rb") as f:
            files = {"file": (Path(pdf_path).name, f, "application/pdf")}
            data = {"configuration": json.dumps(config_payload)}
            response = requests.post(f"{base_url}/upload", headers=headers, files=files, data=data)

        if response.status_code not in [200, 201]:
            print(f"Lỗi upload API (HTTP {response.status_code}): {response.text}")
            return []

        job_id = response.json().get("id")
        print(f"-> Đã đẩy file lên LlamaCloud (Job ID: {job_id}). Đang chờ AI đọc tài liệu...")

        # 2. Chờ xử lý xong và lấy luôn kết quả Markdown qua tham số expand=markdown
        while True:
            # Endpoint chuẩn của v2: /api/v2/parse/{job_id}?expand=markdown
            status_res = requests.get(f"{base_url}/{job_id}", headers=headers, params={"expand": "markdown"})
            
            if status_res.status_code != 200:
                print(f"\nLỗi kiểm tra trạng thái (HTTP {status_res.status_code}): {status_res.text}")
                return []

            res_data = status_res.json()
            job_info = res_data.get("job", res_data)
            status = str(job_info.get("status", "")).upper()

            if status in ["SUCCESS", "COMPLETED"]:
                print("\n-> AI đã đọc xong tài liệu! Đang trích xuất nội dung...")
                break
            elif status in ["ERROR", "FAILED", "CANCELED"]:
                print(f"\nLỗi trong quá trình parse trên server: {res_data}")
                return []
            
            print(".", end="", flush=True)
            time.sleep(2)

        # 3. Map dữ liệu Markdown từ phản hồi của v2 API về chuẩn list dict của hệ thống
        extracted_pages = []
        md_container = res_data.get("markdown", {})
        pages_data = md_container.get("pages", []) if isinstance(md_container, dict) else []
        
        if pages_data:
            for i, page in enumerate(pages_data):
                extracted_pages.append({
                    "page": page.get("page_number") or page.get("page", i + 1),
                    "text": page.get("markdown") or page.get("md") or page.get("text", "")
                })
        elif isinstance(md_container, str) and md_container.strip():
            extracted_pages.append({"page": 1, "text": md_container})

        return extracted_pages

    except Exception as e:
        print(f"\nLỗi kết nối API LlamaParse v2: {e}")
        return []