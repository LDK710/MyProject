import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import BASE_DIR
from src.embedding import embed_documents, embed_query
from src.vector_store import add_chunks, search_chunks, get_collection_count

def run_vector_store_practice():
    chunks_file = BASE_DIR / "data" / "ketqua_chunks.json"
    
    if not chunks_file.exists():
        print(f"Không tìm thấy file {chunks_file}. Hãy chạy main.py để tạo chunks trước!")
        return

    # 1. Đọc dữ liệu chunks đã lưu từ bài trước
    with open(chunks_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    chunks = data.get("chunks", [])
    if not chunks:
        print("Danh sách chunks rỗng!")
        return

    print(f"1. Đã đọc {len(chunks)} chunks từ {chunks_file.name}.")

    # 2. Tách dữ liệu thành 4 mảng song song chuẩn định dạng ChromaDB
    ids = []
    documents = []
    metadatas = []

    for item in chunks:
        # Tạo ID duy nhất kết hợp tên file và chunk_id để tránh trùng khi nạp nhiều tài liệu
        unique_id = f"{item['source_file']}_{item['chunk_id']}"
        ids.append(unique_id)
        documents.append(item["text"])
        
        # Metadata của ChromaDB chỉ chấp nhận kiểu str, int, float, bool (không nhận None)
        metadatas.append({
            "source_file": str(item.get("source_file", "")),
            "page": int(item.get("page", 0)),
            "section_context": str(item.get("section_context", ""))
        })

    # 3. Tạo Vector Embedding cho toàn bộ nội dung chunks
    print("2. Đang tạo Vector Embedding cho các chunks...")
    embeddings = embed_documents(documents)

    # 4. Lưu vào ChromaDB (Persistent Storage)
    print("3. Đang lưu vectors và metadata vào ChromaDB...")
    add_chunks(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    print(f"-> Hoàn tất! Tổng số chunks trong ChromaDB hiện tại: {get_collection_count()}")

    # 5. Nhập câu hỏi và truy vấn 3-5 chunks gần nhất
    user_query = "Tóm tắt nội dung chính của tài liệu này là gì?"

    query_vec = embed_query(user_query)
    results = search_chunks(query_embedding=query_vec, top_k=3)

    print(f"\n=== TOP 3 CHUNKS PHÙ HỢP NHẤT VỚI CÂU HỎI: '{user_query}' ===")
    
    # ChromaDB trả về kết quả dạng list lồng nhau (vì hỗ trợ nhiều query cùng lúc)
    retrieved_docs = results["documents"][0]
    retrieved_metas = results["metadatas"][0]
    retrieved_distances = results["distances"][0]

    for i in range(len(retrieved_docs)):
        # Với không gian 'cosine', ChromaDB trả về Cosine Distance = 1 - Cosine Similarity
        similarity_score = 1 - retrieved_distances[i]
        meta = retrieved_metas[i]
        
        print(f"\n--- Kết quả #{i + 1} (Độ tương đồng: {similarity_score:.4f}) ---")
        print(f"Nguồn: {meta['source_file']} | Trang: {meta['page']} | Mục: {meta['section_context']}")
        print(f"Nội dung:\n{retrieved_docs[i][:300]}...") # In 300 ký tự đầu để kiểm tra

if __name__ == "__main__":
    run_vector_store_practice()