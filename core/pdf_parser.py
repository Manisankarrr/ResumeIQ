import fitz

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a given PDF file in bytes.
    Raises a ValueError if the extracted text length is less than 50 characters.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    text_chunks = []
    for page in doc:
        text_chunks.append(page.get_text())
        
    doc.close()
    
    # Concatenate all text from pages
    raw_text = "".join(text_chunks)
    
    # Strip excessive whitespace by splitting and re-joining
    clean_text = " ".join(raw_text.split())
    
    # Raise error if text is too short
    if len(clean_text) < 50:
        raise ValueError("Extracted text is under 50 characters. Document may be scanned or empty.")
        
    return clean_text

if __name__ == "__main__":
    # Self-contained test block
    print("Running tests for extract_text_from_pdf...")
    
    # 1. Test with a valid length PDF
    test_doc_valid = fitz.open()
    page = test_doc_valid.new_page()
    page.insert_text((50, 50), "This is a sufficiently long string of text to ensure the character count goes over the fifty characters minimum limit.")
    valid_pdf_bytes = test_doc_valid.tobytes()
    test_doc_valid.close()
    
    try:
        text = extract_text_from_pdf(valid_pdf_bytes)
        print(f"SUCCESS: Extracted valid PDF. Length: {len(text)} characters.")
        print(f"Content: '{text}'\n")
    except Exception as e:
        print(f"FAIL: Unexpected error on valid PDF: {e}\n")
        
    # 2. Test with a short/invalid length PDF
    test_doc_invalid = fitz.open()
    page2 = test_doc_invalid.new_page()
    page2.insert_text((50, 50), "Too short.")
    invalid_pdf_bytes = test_doc_invalid.tobytes()
    test_doc_invalid.close()
    
    try:
        extract_text_from_pdf(invalid_pdf_bytes)
        print("FAIL: The function did not raise a ValueError for a short PDF.\n")
    except ValueError as e:
        print(f"SUCCESS: Caught expected ValueError for short PDF: '{e}'\n")
