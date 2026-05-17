import pypdf

def extract_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

if __name__ == "__main__":
    print(extract_text("SHL_AI_Intern_Assignment (1).pdf"))
