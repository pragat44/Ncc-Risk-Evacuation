import fitz

def parse_contract_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    segments = [seg.strip() for seg in text.split("\n") if len(seg.strip()) > 30]
    return segments
