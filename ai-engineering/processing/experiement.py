from docling.document_converter import DocumentConverter
from pathlib import Path


# Set base directory to the project root
BASE_DIR = Path(__file__).resolve().parent.parent

pdf_path = BASE_DIR / "data" / "raw" / "reglementation" / "Reglement-Etudes-ESI-Ingenieur-Masters-Doctorat-Mars-2023.pdf"
# pdf_path = Path(__file__).resolve().parent / "doc.pdf"
output_dir = BASE_DIR / "data" / "clean"

converter = DocumentConverter()
result = converter.convert(pdf_path)
markdown = result.document.export_to_markdown()

with open(output_dir / f"{pdf_path.stem}.md", "w", encoding="utf-8") as f:
    f.write(markdown)
