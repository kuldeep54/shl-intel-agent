import PyPDF2
import sys

def extract_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    pdf_file = "d:/Agent/SHL_AI_Intern_Assignment (1).pdf"
    print(extract_text(pdf_file))
