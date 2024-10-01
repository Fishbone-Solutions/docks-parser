import streamlit as st
from docx import Document
import csv
import io

def extract_h3_clauses(docx_file):
    document = Document(docx_file)
    clauses = []
    
    for paragraph in document.paragraphs:
        if paragraph.style.name == 'Heading 3' and paragraph.text.strip():
            # Assuming the clause number is the initial part of the heading
            parts = paragraph.text.split('\t', 1)  # Split on tab character for clause number
            if len(parts) == 2:
                clause_number = parts[0].strip()
                clause_content = parts[1].strip()
                clauses.append((clause_number, clause_content))
    
    return clauses

def save_to_csv(clauses):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Clause Number', 'Clause Content'])  # Header
    writer.writerows(clauses)
    
    output.seek(0)  # Move to the beginning of the StringIO buffer
    return output.getvalue()

def main():
    st.title("🐠 Clause Extractor from DOCX")

    # File uploader widget
    uploaded_file = st.file_uploader("Choose a DOCX file", type=["docx"])

    if uploaded_file is not None:
        # Display file details
        st.write("Filename:", uploaded_file.name)
        st.write("File type:", uploaded_file.type)
        st.write("File size (bytes):", uploaded_file.size)

        # Extract H3 clauses
        clauses = extract_h3_clauses(uploaded_file)
        
        if clauses:
            st.write("Extracted H3 Clauses:")
            for clause in clauses:
                st.write(f"{clause[0]}: {clause[1]}")

            # Save to CSV
            csv_data = save_to_csv(clauses)
            st.success("H3 clauses have been saved to a CSV format.")

            # Provide a download button for the CSV
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name='h3_clauses.csv',
                mime='text/csv'
            )
        else:
            st.warning("No H3 clauses found in the document.")

if __name__ == "__main__":
    main()