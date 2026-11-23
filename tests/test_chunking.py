import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.chunking import chunk_document_optimal

class TestChunking(unittest.TestCase):
    def test_hybrid_markdown_chunking(self):
        sample_pages = [
            {
                "page": 5,
                "text": (
                    "# Chương 1: Tổng quan AI\n"
                    "Trí tuệ nhân tạo đang phát triển mạnh mẽ.\n"
                    "## 1.1 Học máy (Machine Learning)\n"
                    "Machine Learning là một nhánh quan trọng của AI giúp máy tính tự học từ dữ liệu."
                )
            }
        ]

        chunks = chunk_document_optimal(
            pages=sample_pages,
            source_file="giao_trinh.pdf",
            chunk_size=100,
            chunk_overlap=20
        )

        # Kiểm tra có tạo ra chunks và giữ đúng metadata trang
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(chunk["page"], 5)
            self.assertEqual(chunk["source_file"], "giao_trinh.pdf")

        # Kiểm tra chunk thuộc mục 1.1 có nhận diện đúng ngữ cảnh tiêu đề cha không
        sub_section_chunks = [c for c in chunks if "1.1 Học máy" in c["section_context"]]
        self.assertTrue(len(sub_section_chunks) > 0)
        self.assertEqual(
            sub_section_chunks[0]["section_context"],
            "Chương 1: Tổng quan AI > 1.1 Học máy (Machine Learning)"
        )

if __name__ == "__main__":
    unittest.main()