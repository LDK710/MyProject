from pathlib import Path
from src.config import DATA_DIR
from src.pdf_loader import extract_pdf
from src.text_cleaner import remove_empty_pages, validate_document
from src.file_handler import save_json, load_json
from src.chunking import chunk_document_optimal
from src.embedding import embed_documents, embed_query
from src.vector_store import add_chunks, search_chunks, get_collection_count

def ingest_pdf_pipeline(pdf_path: Path, force_reprocess: bool = False):
    """
    Luồng nạp và lập chỉ mục tài liệu PDF vào Vector Database (ChromaDB):
    1. Trích xuất PDF -> Markdown (hoặc dùng lại cache JSON nếu đã xử lý trước đó).
    2. Làm sạch và kiểm tra tính toàn vẹn dữ liệu.
    3. Chia chunks theo cấu trúc Markdown + đệ quy ký tự.
    4. Vector hóa và lưu bền vững vào ChromaDB.
    """
    if not pdf_path.exists():
        print(f"[Lỗi] Không tìm thấy file PDF tại: {pdf_path}")
        return False

    cleaned_json_path = DATA_DIR / f"{pdf_path.stem}_cleaned.json"
    chunks_json_path = DATA_DIR / f"{pdf_path.stem}_chunks.json"

    # Bước 1 & 2: Trích xuất & Làm sạch (Tận dụng file JSON đã lưu để tiết kiệm API LlamaCloud)
    if cleaned_json_path.exists() and not force_reprocess:
        print(f"[Bước 1-2] Phát hiện dữ liệu đã làm sạch tại '{cleaned_json_path.name}'. Đang tải lại...")
        cleaned_pages = load_json(cleaned_json_path)
    else:
        print(f"[Bước 1] Đang trích xuất nội dung PDF từ '{pdf_path.name}' qua LlamaParse...")
        raw_pages = extract_pdf(pdf_path)
        if not raw_pages:
            print("[Dừng] Không trích xuất được dữ liệu từ PDF.")
            return False

        print("[Bước 2] Đang làm sạch và kiểm tra dữ liệu...")
        cleaned_pages = remove_empty_pages(raw_pages)
        is_valid, msg = validate_document(cleaned_pages)
        if not is_valid:
            print(f"[Dừng] {msg}")
            return False

        print(f"-> {msg}")
        save_json(cleaned_pages, cleaned_json_path)

    # Bước 3: Chia nhỏ văn bản (Hybrid MarkdownHeader + RecursiveCharacter)
    print(f"\n[Bước 3] Đang chia chunks tối ưu cho '{pdf_path.name}'...")
    chunks = chunk_document_optimal(
        pages=cleaned_pages,
        source_file=pdf_path.name,
        chunk_size=1000,
        chunk_overlap=150
    )
    save_json({
        "source_file": pdf_path.name,
        "total_chunks": len(chunks),
        "chunks": chunks
    }, chunks_json_path)
    print(f"-> Đã tạo {len(chunks)} chunks.")

    # Bước 4: Chuẩn bị dữ liệu và tạo Vector Embedding
    print("\n[Bước 4] Đang vector hóa các chunks bằng mô hình multilingual-e5-small...")
    ids = [f"{item['source_file']}_{item['chunk_id']}" for item in chunks]
    documents = [item["text"] for item in chunks]
    metadatas = [
        {
            "source_file": str(item.get("source_file", "")),
            "page": int(item.get("page", 0)),
            "section_context": str(item.get("section_context", ""))
        }
        for item in chunks
    ]

    embeddings = embed_documents(documents)

    # Bước 5: Lưu vào ChromaDB (Persistent Storage)
    print("[Bước 5] Đang lưu vectors và metadata vào ChromaDB...")
    add_chunks(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    print(f"-> Hoàn tất nạp dữ liệu! Tổng số chunks trong ChromaDB: {get_collection_count()}")
    return True


def interactive_search_loop(top_k: int = 3):
    """
    Vòng lặp cho phép người dùng nhập câu hỏi liên tục và truy xuất các đoạn tài liệu liên quan nhất.
    """
    print("\n" + "=" * 60)
    print("HỆ THỐNG TÌM KIẾM NGỮ NGHĨA TÀI LIỆU (Gõ 'exit' hoặc 'q' để thoát)")
    print("=" * 60)

    while True:
        query = input("\nNhập câu hỏi của bạn: ").strip()
        if not query:
            continue
        if query.lower() in ["exit", "quit", "q"]:
            print("Đã thoát chương trình.")
            break

        # Chuyển câu hỏi thành vector và truy vấn ChromaDB
        query_vec = embed_query(query)
        results = search_chunks(query_embedding=query_vec, top_k=top_k)

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        if not docs:
            print("-> Không tìm thấy đoạn thông tin nào phù hợp trong cơ sở dữ liệu.")
            continue

        print(f"\n--- TOP {len(docs)} ĐOẠN THÔNG TIN LIÊN QUAN NHẤT ---")
        for i in range(len(docs)):
            similarity = 1 - distances[i]
            meta = metas[i]
            section_info = f" | Mục: {meta['section_context']}" if meta.get("section_context") else ""

            print(f"\n[{i + 1}] Độ tương đồng: {similarity:.4f} | File: {meta['source_file']} | Trang: {meta['page']}{section_info}")
            print("-" * 50)
            print(docs[i])


def main():
    # Thay đổi tên file PDF của bạn nằm trong thư mục data/ tại đây
    target_pdf = DATA_DIR / "Buoi_1_AI_Engineering_2026.pptx.pdf"

    # Chạy pipeline nạp tài liệu (đặt force_reprocess=True nếu muốn gọi lại LlamaParse từ đầu)
    success = ingest_pdf_pipeline(pdf_path=target_pdf, force_reprocess=False)

    # Nếu nạp thành công (hoặc DB đã có sẵn dữ liệu), mở giao diện đặt câu hỏi
    if success or get_collection_count() > 0:
        interactive_search_loop(top_k=3)


if __name__ == "__main__":
    main()