# app.py
import streamlit as st
import spacy
import pandas as pd

# Load the biomedical NER model
nlp_bc = en_core_med7_trf.load()

# Function to extract entities from the transcription
def extract_entities(transcription):
    doc = nlp_bc(transcription)
    entities_info = []
    for ent in doc.ents:
        entities_info.append({
            "Text": ent.text,
            "Start": ent.start_char,
            "End": ent.end_char,
            "Label": ent.label_
        })
    return entities_info

# Main function to run the Streamlit app
def main():
    st.title("Biomedical Entity Extraction")
    st.write("Enter your transcription below:")

    # Text input for transcription
    transcription = st.text_area("Transcription:")

    if transcription:
        # Extract entities from the transcription
        entities = extract_entities(transcription)

        if entities:
            # Display entity information in a table
            st.subheader("Entities Information:")
            st.write(pd.DataFrame(entities))

if __name__ == "__main__":
    main()
