from pathlib import Path
import io

import fitz  # PyMuPDF
from docling.document_converter import DocumentConverter


def docs_to_markdown(pdf_path: Path, output_dir: Path, batch_size: int = 10) -> bool:
    """
    Convert a large PDF to Markdown in batches of `batch_size` pages by:
        - reading page ranges with PyMuPDF,
        - building small in-memory PDFs for each batch,
        - converting each batch with Docling,
        - appending the resulting Markdown to a single output file.

    No intermediate PDF files are written to disk.

    Args:
        pdf_path (Path): Path to the source PDF.
        output_dir (Path): Directory where the final Markdown file is written.
        batch_size (int): Number of pages per batch (default: 10).

    Returns:
        bool: True on success, False if any step fails.
    """
    # --- Sanity checks -------------------------------------------------------
    try:
        if not pdf_path.is_file():
            raise FileNotFoundError(f"The specified PDF file does not exist: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
        return False

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory {output_dir}: {e}")
        return False

    output_file = output_dir / f"{pdf_path.stem}.md"

    # Remove existing output file if present
    if output_file.exists():
        try:
            output_file.unlink()
        except Exception as e:
            print(f"Error occurred while deleting existing Markdown file: {e}")
            return False

    # --- Open source PDF & initialize Docling converter ---------------------
    try:
        src_doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF with PyMuPDF: {e}")
        return False

    page_count = src_doc.page_count

    try:
        converter = DocumentConverter()
    except Exception as e:
        print(f"Error initializing DocumentConverter: {e}")
        src_doc.close()
        return False

    # --- Process in page batches --------------------------------------------
    try:
        # Create / truncate the output file once
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write("")

        for start_index in range(0, page_count, batch_size):
            end_index = min(start_index + batch_size, page_count)
            print(f"Processing pages {start_index + 1}-{end_index} of {page_count}...")

            # 1) Build a small in-memory PDF containing just this page range
            batch_pdf_bytes_io = io.BytesIO()
            try:
                batch_doc = fitz.open()  # empty PDF
                batch_doc.insert_pdf(
                    src_doc,
                    from_page=start_index,
                    to_page=end_index - 1,
                )
                batch_doc.save(batch_pdf_bytes_io)
                batch_doc.close()
            except Exception as e:
                print(f"Error creating in-memory batch PDF for pages {start_index + 1}-{end_index}: {e}")
                src_doc.close()
                return False

            batch_pdf_bytes_io.seek(0)
            batch_pdf_bytes = batch_pdf_bytes_io.read()

            # 2) Convert this in-memory PDF with Docling
            try:
                result = converter.convert(batch_pdf_bytes)
                md_batch = result.document.export_to_markdown()
            except Exception as e:
                print(f"Error converting batch pages {start_index + 1}-{end_index} with Docling: {e}")
                src_doc.close()
                return False

            # 3) Append batch markdown to final file
            try:
                with open(output_file, "a", encoding="utf-8") as f_out:
                    if start_index != 0:
                        f_out.write("\n\n")  # separator between batches
                    f_out.write(md_batch)
            except Exception as e:
                print(f"Error writing Markdown for pages {start_index + 1}-{end_index}: {e}")
                src_doc.close()
                return False

    except Exception as e:
        print(f"Unexpected error during batched processing: {e}")
        src_doc.close()
        return False
    finally:
        src_doc.close()

    print(f"Markdown successfully written to {output_file}")
    return True