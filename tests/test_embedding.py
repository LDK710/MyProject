import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào sys.path để import được module từ thư mục src/
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.embedding import embed_documents, embed_query

def run_similarity_test():
    # Danh sách 5 câu mẫu cần kiểm tra độ tương đồng
    sentences = [
        "Trí tuệ nhân tạo là gì?",
        "AI được ứng dụng như thế nào?",
        "Machine Learning có liên quan gì đến AI?",
        "Python là ngôn ngữ lập trình gì?",
        "Cấu trúc dữ liệu là gì?"
    ]

    print("1. Đang chuyển đổi 5 câu sang Vector Embedding...")
    doc_embeddings = embed_documents(sentences)
    print(f"-> Hoàn tất! Kích thước mỗi vector: {doc_embeddings.shape[1]} chiều.\n")

    # Tính ma trận Cosine Similarity giữa các cặp câu (do vector đã chuẩn hóa nên dùng tích vô hướng @)
    similarity_matrix = doc_embeddings @ doc_embeddings.T

    # So sánh câu gốc số 1 với tất cả 5 câu
    base_idx = 0
    print(f"=== SO SÁNH ĐỘ TƯƠNG ĐỒNG VỚI CÂU: '{sentences[base_idx]}' ===")
    scores = sorted(enumerate(similarity_matrix[base_idx]), key=lambda x: x[1], reverse=True)

    for idx, score in scores:
        print(f"Cosine Score: {score:.4f}  |  {sentences[idx]}")

    # Thử nghiệm Semantic Search với câu hỏi không trùng từ khóa
    user_query = "Học máy đóng vai trò gì trong lĩnh vực trí thông minh nhân tạo?"
    query_vec = embed_query(user_query)
    search_scores = doc_embeddings @ query_vec

    print(f"\n=== THỬ NGHIỆM SEMANTIC SEARCH ===")
    print(f"Câu hỏi: '{user_query}'")
    ranked_results = sorted(enumerate(search_scores), key=lambda x: x[1], reverse=True)

    for rank, (idx, score) in enumerate(ranked_results, start=1):
        print(f"Top {rank} (Điểm {score:.4f}): {sentences[idx]}")

if __name__ == "__main__":
    run_similarity_test()