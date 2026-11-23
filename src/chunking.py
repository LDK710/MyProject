from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def chunk_document_optimal(pages, source_file, chunk_size=1000, chunk_overlap=150):
    """
    Tối ưu cho cả Slide bài giảng và Tài liệu dài:
    - Nếu cả trang <= chunk_size: Giữ nguyên toàn bộ trang thành 1 chunk để không làm vụn ý trên slide.
    - Nếu trang > chunk_size: Chia theo cấu trúc tiêu đề Markdown + Đệ quy ký tự.
    """
    headers_to_split_on = [
        ("#", "Header_1"),
        ("##", "Header_2"),
        ("###", "Header_3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []
    chunk_global_id = 1

    for page_item in pages:
        page_num = page_item.get("page")
        page_text = page_item.get("text", "").strip()

        if not page_text:
            continue

        # Lấy tiêu đề đầu tiên trên trang (nếu có) làm ngữ cảnh tổng quát cho trang
        first_line_header = ""
        for line in page_text.splitlines():
            if line.lstrip().startswith("#"):
                first_line_header = line.lstrip("#").strip().replace("*", "")
                break

        # TRƯỜNG HỢP 1: Trang ngắn (như Slide bài giảng) -> Giữ nguyên trọn vẹn 1 trang = 1 chunk
        if len(page_text) <= chunk_size:
            all_chunks.append({
                "chunk_id": f"chunk_{chunk_global_id:04d}",
                "source_file": source_file,
                "page": page_num,
                "section_context": first_line_header,
                "chunk_index_on_page": 1,
                "char_count": len(page_text),
                "text": page_text
            })
            chunk_global_id += 1
            continue

        # TRƯỜNG HỢP 2: Trang dài (như sách/báo cáo) -> Chia theo Markdown + Đệ quy
        md_header_docs = markdown_splitter.split_text(page_text)
        final_docs = recursive_splitter.split_documents(md_header_docs)

        for idx, doc in enumerate(final_docs):
            section_context = " > ".join(
                [v.replace("*", "") for k, v in doc.metadata.items() if k.startswith("Header_")]
            ) or first_line_header

            all_chunks.append({
                "chunk_id": f"chunk_{chunk_global_id:04d}",
                "source_file": source_file,
                "page": page_num,
                "section_context": section_context,
                "chunk_index_on_page": idx + 1,
                "char_count": len(doc.page_content),
                "text": doc.page_content
            })
            chunk_global_id += 1

    return all_chunks