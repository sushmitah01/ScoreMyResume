import pdfplumber
import docx


def extract_text_from_pdf(file_path):
    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def extract_text_from_docx(file_path):
    document = docx.Document(file_path)
    text_parts = [paragraph.text for paragraph in document.paragraphs]
    return "\n".join(text_parts)


def parse_resume(file_path):
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")