import spacy
import streamlit as st
from spacy.matcher import Matcher
from PyPDF2 import PdfReader

# Load the custom medical NER model
model_path = "en_ner_bc5cdr_md-0.5.1"
nlp_bc = spacy.load(model_path)

# Initialize Matcher for identifying drug doses
matcher = Matcher(nlp_bc.vocab)
pattern = [{'ENT_TYPE': 'CHEMICAL'}, {'LIKE_NUM': True}, {'IS_ASCII': True}]
matcher.add("DRUG_DOSE", [pattern])

# Function to perform NER and identify entities
def perform_ner(text):
    doc = nlp_bc(text)
    entities = []
    drug_doses = []
    for ent in doc.ents:
        entities.append((ent.label_, ent.text))
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        drug_doses.append((nlp_bc.vocab.strings[match_id], span.text))
    return entities, drug_doses

# Streamlit app
def main():
    st.title("Medical NER from PDF")
    st.write("Upload a PDF file to extract text and identify medical entities.")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file is not None:
        # Read PDF file
        text = ""
        with st.spinner("Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_file)

        st.write("### Extracted Text:")
        st.write(text)

        # Perform NER
        with st.spinner("Performing NER..."):
            entities, drug_doses = perform_ner(text)

        # Display identified entities
        st.write("### Identified Entities:")
        for label, entity in entities:
            st.write(f"- {label}: {entity}")

        # Display identified drug doses
        st.write("### Identified Drug Doses:")
        for label, dose in drug_doses:
            st.write(f"- {label}: {dose}")

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with st.spinner("Extracting text from PDF..."):
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Call the main function
main()
