import PyPDF2
import sys

def extract_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(min(5, len(reader.pages))): # Just first 5 pages for catalog
                text += reader.pages[page_num].extract_text()
            return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    pdf_file = "d:/Agent/shl_product_catalog.pdf"
    print(extract_text(pdf_file))
