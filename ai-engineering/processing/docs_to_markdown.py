from docling.document_converter import (
    DocumentConverter,
    ConversionParameters,
    PageRange,
)
from pathlib import Path
import fitz  # PyMuPDF, just to get page count safely


def docs_to_markdown(pdf_path: Path, output_dir: Path, batch_size: int = 10) -> bool:
    """
    Convert a large PDF document to Markdown format in page batches and
    save it to the specified output directory.

    The PDF is processed in batches of `batch_size` pages (default: 10)
    using Docling's PageRange, to reduce memory usage on very large PDFs.

    Args:
        pdf_path (Path): The path to the PDF document to be converted.
        output_dir (Path): The directory where the converted Markdown file will be saved.
        batch_size (int): Number of pages per Docling conversion batch.

    Returns:
        bool: True if the conversion and saving are successful, False otherwise.
    """
    # --- Basic checks ---
    try:
        if not pdf_path.is_file():
            raise FileNotFoundError(f"The specified PDF file does not exist: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
        return False

    # Create output dir if needed
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

    # --- Get total page count (using PyMuPDF) ---
    try:
        with fitz.open(pdf_path) as doc:
            page_count = doc.page_count
    except Exception as e:
        print(f"Error opening PDF to get page count: {e}")
        return False

    # --- Initialize converter once ---
    try:
        converter = DocumentConverter()
    except Exception as e:
        print(f"Error initializing DocumentConverter: {e}")
        return False

    # --- Process in batches of `batch_size` pages ---
    # Docling PageRange is usually 1-based (start/end inclusive)
    try:
        with open(output_file, "w", encoding="utf-8") as f_out:
            # Optional: write a header or initial newline if you like
            f_out.write("")  # start clean

        for start_page in range(1, page_count + 1, batch_size):
            end_page = min(start_page + batch_size - 1, page_count)

            print(f"Processing pages {start_page}-{end_page} of {page_count}...")

            params = ConversionParameters(
                page_range=PageRange(start=start_page, end=end_page)
            )

            try:
                result = converter.convert(pdf_path, parameters=params)
                markdown_batch = result.document.export_to_markdown()
            except Exception as e:
                # Log the batch that failed and continue or abort.
                # Here we abort and return False; you could choose to skip instead.
                print(f"Error converting pages {start_page}-{end_page}: {e}")
                return False

            # Append this batch's markdown to the output file
            try:
                with open(output_file, "a", encoding="utf-8") as f_out:
                    # separate batches with blank lines so they don't run together
                    if start_page != 1:
                        f_out.write("\n\n")
                    f_out.write(markdown_batch)
            except Exception as e:
                print(f"Error occurred while saving Markdown for pages {start_page}-{end_page}: {e}")
                return False

    except Exception as e:
        print(f"Unexpected error during batched processing: {e}")
        return False

    print(f"Markdown successfully written to {output_file}")
    return True