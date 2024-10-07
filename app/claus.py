import streamlit as st
import pandas as pd
from docx import Document
import re
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Function to extract clause numbers and content, including nested and sub-clauses
def extract_clauses(doc):
    clauses = []
    current_clause = None
    current_text = []
    sub_clause = None
    sub_clause_text = []
    sub_sub_clause = None
    sub_sub_clause_text = []
    
    for para in doc.paragraphs:
        text = para.text.strip()

        # Match main clauses (e.g., 1, 1.1, 1.1.1, etc.)
        match = re.match(r'^(\d+(\.\d+)*)(\.\d+)*\s*(.*)', text)
        # Match sub-clauses like a), b)
        sub_match = re.match(r'^([a-z]\))\s*(.*)', text)
        # Match sub-sub-clauses like i), ii), etc.
        sub_sub_match = re.match(r'^([ivxlc]+)\)\s*(.*)', text)

        if match:
            # Save the previous clause and sub-clauses if present
            if current_clause:
                if sub_clause:
                    if sub_sub_clause:
                        clauses.append((f"{current_clause} {sub_clause} {sub_sub_clause}", " ".join(sub_sub_clause_text)))
                        sub_sub_clause = None
                        sub_sub_clause_text = []
                    clauses.append((f"{current_clause} {sub_clause}", " ".join(sub_clause_text)))
                    sub_clause = None
                    sub_clause_text = []
                clauses.append((current_clause, " ".join(current_text)))
            
            # Start a new clause
            current_clause = match.group(1)
            current_text = [match.group(4)]  # Clause content starts

        elif sub_match:
            # Save the previous sub-clause if present
            if sub_clause:
                if sub_sub_clause:
                    clauses.append((f"{current_clause} {sub_clause} {sub_sub_clause}", " ".join(sub_sub_clause_text)))
                    sub_sub_clause = None
                    sub_sub_clause_text = []
                clauses.append((f"{current_clause} {sub_clause}", " ".join(sub_clause_text)))

            # Start a new sub-clause
            sub_clause = sub_match.group(1)
            sub_clause_text = [sub_match.group(2)]
        
        elif sub_sub_match:
            # Save sub-sub clauses like i), ii)
            if sub_sub_clause:
                clauses.append((f"{current_clause} {sub_clause} {sub_sub_clause}", " ".join(sub_sub_clause_text)))
            sub_sub_clause = sub_sub_match.group(1)
            sub_sub_clause_text = [sub_sub_match.group(2)]
        
        else:
            # Append to the current clause's content if no new clause is found
            if sub_sub_clause:
                sub_sub_clause_text.append(text)
            elif sub_clause:
                sub_clause_text.append(text)
            else:
                current_text.append(text)
    
    # Add the last clauses
    if current_clause:
        if sub_clause:
            if sub_sub_clause:
                clauses.append((f"{current_clause} {sub_clause} {sub_sub_clause}", " ".join(sub_sub_clause_text)))
            clauses.append((f"{current_clause} {sub_clause}", " ".join(sub_clause_text)))
        clauses.append((current_clause, " ".join(current_text)))
    
    return clauses

# Streamlit app layout
st.set_page_config(layout="wide")  # Set wide layout to utilize the full screen

st.title("Editable Clause Extraction Tool with AgGrid")
st.write("Upload a .docx file, and edit the content in the table. You can also add/remove rows.")

# File uploader
uploaded_file = st.file_uploader("Upload a DOCX file", type="docx")

if uploaded_file is not None:
    # Load the .docx file
    doc = Document(uploaded_file)
    
    # Extract clauses and content
    clauses = extract_clauses(doc)
    
    # Convert to DataFrame
    df = pd.DataFrame(clauses, columns=["Clause Number", "Content"])

    # Configure AgGrid options for editable table
    st.subheader("Edited Clauses Table")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
    gb.configure_default_column(editable=True)  # Make all columns editable
    gb.configure_grid_options(getRowNodeId="Clause Number")  # Enable row ID for rows

    # Set the columns to auto-fit the available space
    gb.configure_auto_height()  # Dynamically adjust row height based on content
    gb.configure_default_column(resizable=True)  # Allow column resizing

    # Build the grid options
    gridOptions = gb.build()

    # Display the AgGrid table and make it use the full screen width
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,  # Capture value changes
        height=600,  # Adjust the height as needed
        fit_columns_on_grid_load=True,  # Adjust columns to fit the width
        enable_enterprise_modules=True,  # Enables features like row/column addition
    )

    # Retrieve the updated DataFrame
    updated_df = pd.DataFrame(grid_response["data"])

    # Display the edited DataFrame
    st.write("Edited Clauses Table:")
    st.dataframe(updated_df, use_container_width=True)  # Ensure full width

    # Download the updated table as CSV
    csv = updated_df.to_csv(index=False)
    st.download_button(label="Download CSV", data=csv, file_name="edited_clauses.csv", mime="text/csv")
