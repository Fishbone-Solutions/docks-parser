import streamlit as st
from docx import Document
import csv
import io

def extract_clauses(docx_file):
    document = Document(docx_file)
    clauses = []
    current_clause = None
    nested_items = []

    for paragraph in document.paragraphs:
        # Check if the paragraph is a list item
        if paragraph.style.name.startswith('List'):
            if current_clause:
                nested_items.append(paragraph.text.strip())
            continue
        
        # If we encounter a new heading or a new clause
        if current_clause:
            # Add the nested items to the current clause if any exist
            if nested_items:
                current_clause[1] += " " + " ".join(nested_items)
                nested_items = []

            clauses.append(current_clause)
            current_clause = None

        # Check for clause headings (assuming they are not styled as H3)
        if paragraph.text.strip():
            parts = paragraph.text.split('\t', 1)  # Split on tab character
            if len(parts) == 2:
                clause_number = parts[0].strip()
                clause_content = parts[1].strip()
                current_clause = [clause_number, clause_content]
    
    # Add the last clause if it exists
    if current_clause:
        if nested_items:
            current_clause[1] += " " + " ".join(nested_items)
        clauses.append(current_clause)

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

        # Extract clauses
        clauses = extract_clauses(uploaded_file)
        
        if clauses:
            st.write("Extracted Clauses:")
            for clause in clauses:
                st.write(f"{clause[0]}: {clause[1]}")

            # Save to CSV
            csv_data = save_to_csv(clauses)
            st.success("Clauses have been saved to a CSV format.")

            # Provide a download button for the CSV
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name='clauses.csv',
                mime='text/csv'
            )
        else:
            st.warning("No clauses found in the document.")

if __name__ == "__main__":
    main()