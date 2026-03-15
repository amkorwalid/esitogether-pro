from docling.document_converter import DocumentConverter
from pathlib import Path

def docs_to_markdown(pdf_path: Path, output_dir: Path):
    """
    Convert a PDF document to Markdown format and save it to the specified output directory.
    Args:
        pdf_path (Path): The path to the PDF document to be converted.
        output_dir (Path): The directory where the converted Markdown file will be saved.
        
    Returns:
        bool: True if the conversion and saving are successful, False otherwise.
    """
    try:
        if not pdf_path.is_file():
            raise FileNotFoundError(f"The specified PDF file does not exist: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
        return False

    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        markdown = result.document.export_to_markdown()
        
    except Exception as e:
        print(f"Error: {e}")
        return False

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    try:
        with open(output_dir / f"{pdf_path.stem}.md", "w", encoding="utf-8") as f:
            f.write(markdown)
    except Exception as e:
        print(f"Error occurred while saving Markdown file: {e}")
        return False
    
    return True


