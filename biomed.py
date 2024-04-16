import spacy
import streamlit as st
from spacy.matcher import Matcher
from PyPDF2 import PdfReader
import requests
import os
import tarfile

# Function to perform NER and identify entities
def perform_ner(text, nlp_bc, matcher):
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

        # Download and load the custom medical NER model
        model_url = "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_ner_bc5cdr_md-0.5.4.tar.gz"
        model_path = download_and_extract_model(model_url)
        nlp_bc = spacy.load(model_path)

        # Initialize Matcher for identifying drug doses
        matcher = Matcher(nlp_bc.vocab)
        pattern = [{'ENT_TYPE': 'CHEMICAL'}, {'LIKE_NUM': True}, {'IS_ASCII': True}]
        matcher.add("DRUG_DOSE", [pattern])

        # Perform NER
        with st.spinner("Performing NER..."):
            entities, drug_doses = perform_ner(text, nlp_bc, matcher)

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

# Function to download and extract the model
def download_and_extract_model(model_url):
    st.write("Downloading and extracting spaCy model...")
    model_archive_path = "model.tar.gz"
    response = requests.get(model_url)
    with open(model_archive_path, "wb") as f:
        f.write(response.content)
    
    # Extract the model archive
    with tarfile.open(model_archive_path, "r:gz") as tar:
        # Extract all contents to a temporary directory
        temp_dir = "temp_model"
        tar.extractall(temp_dir)
    
    # Find the directory containing the model files
    model_dir = None
    for root, dirs, files in os.walk(temp_dir):
        if "vocab" in dirs and "meta.json" in files and "tokenizer" in dirs:
            model_dir = root
            break
    
    if model_dir is None:
        raise ValueError("Unable to locate model files within the extracted archive.")
    
    st.write("Model downloaded and extracted successfully.")
    return model_dir

# Call the main function
if __name__ == "__main__":
    main()
