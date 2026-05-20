import io
import pytest
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, NumberObject, StreamObject
from application.pdf_extractor import extract_text_from_bytes


def make_pdf_bytes(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    content = f"BT /F1 12 Tf 100 700 Td ({text}) Tj ET".encode()
    stream = StreamObject()
    stream._data = content
    stream[NameObject("/Length")] = NumberObject(len(content))
    page[NameObject("/Contents")] = writer._add_object(stream)

    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})
    })

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_extract_text_returns_expected_content():
    pdf_bytes = make_pdf_bytes("Hola Mundo")
    result = extract_text_from_bytes(pdf_bytes)
    assert "Hola Mundo" in result


def test_extract_text_never_writes_to_disk(tmp_path):
    pdf_bytes = make_pdf_bytes("Sin disco")
    before = list(tmp_path.iterdir())
    extract_text_from_bytes(pdf_bytes)
    after = list(tmp_path.iterdir())
    assert before == after
