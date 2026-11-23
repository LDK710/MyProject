import chromadb
from src.config import DATA_DIR

# Đường dẫn lưu trữ bền vững trên ổ cứng
CHROMA_PATH = str(DATA_DIR / "chroma_db")

# Khởi tạo PersistentClient để dữ liệu không bị mất khi tắt chương trình
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Tạo hoặc mở Collection với không gian đo lường Cosine
collection = client.get_or_create_collection(
    name="study_documents",
    metadata={"hnsw:space": "cosine"}
)

def add_chunks(ids, documents, embeddings, metadatas):
    """
    Lưu (hoặc cập nhật nếu trùng ID) danh sách các chunks, vectors và metadata vào ChromaDB.
    """
    # Chuyển đổi numpy array sang list chuẩn của Python nếu cần
    embeddings_list = embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings_list,
        metadatas=metadatas
    )

def search_chunks(query_embedding, top_k=5):
    """
    Tìm kiếm top_k chunks có ngữ nghĩa gần nhất với query_embedding.
    """
    query_vec = query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding

    return collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

def get_collection_count():
    """Kiểm tra tổng số chunks hiện đang lưu trong database."""
    return collection.count()