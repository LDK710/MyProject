import pymupdf
def extract_pdf(file_path):
    result = []

    doc = pymupdf.open(file_path)

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")

        result.append({
            "page": page_number,
            "text": text
        })

    doc.close()
    return result