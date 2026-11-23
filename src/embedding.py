from sentence_transformers import SentenceTransformer

print("Đang khởi tạo/tải mô hình multilingual-e5-small (lần đầu sẽ mất 1-2 phút)...")
model = SentenceTransformer("intfloat/multilingual-e5-small")
print("-> Đã tải xong mô hình!")

def embed_documents(texts):
    return model.encode(
        ["passage: " + text for text in texts],
        normalize_embeddings=True
    )

def embed_query(query):
    return model.encode(
        ["query: " + query],
        normalize_embeddings=True
    )[0]