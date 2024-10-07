import streamlit as st
import pandas as pd
from docx import Document
import re

# Function to extract clause numbers and content
def extract_clauses(doc):
    clauses = []
    current_clause = None
    current_text = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # Match clause numbers (e.g., 1.1.1, 2.3.5, etc.)
        match = re.match(r'^(\d+(\.\d+)+)\s*(.*)', text)
        if match:
            # Save previous clause if present
            if current_clause:
                clauses.append((current_clause, " ".join(current_text)))
            # Start a new clause
            current_clause = match.group(1)
            current_text = [match.group(3)]  # Clause content starts
        else:
            # Append to current clause's content if no new clause number found
            current_text.append(text)
    
    # Add last clause
    if current_clause:
        clauses.append((current_clause, " ".join(current_text)))
    
    return clauses

# Streamlit app
st.title("Clause Extraction Tool")
st.write("Upload a .docx file and extract clauses and content into a CSV.")

# File uploader
uploaded_file = st.file_uploader("Upload a DOCX file", type="docx")

if uploaded_file is not None:
    # Load the .docx file
    doc = Document(uploaded_file)
    
    # Extract clauses and content
    clauses = extract_clauses(doc)
    
    # Convert to DataFrame
    df = pd.DataFrame(clauses, columns=["Clause Number", "Content"])
    
    # Display the DataFrame
    st.write("Extracted Clauses:")
    st.dataframe(df)
    
    # Download CSV
    csv = df.to_csv(index=False)
    st.download_button(label="Download CSV", data=csv, file_name="clauses.csv", mime="text/csv")
