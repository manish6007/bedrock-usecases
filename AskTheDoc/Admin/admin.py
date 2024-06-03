import boto3
import streamlit as st
import os
import uuid

## s3_client
s3_client = boto3.client("s3")
BUCKET_NAME = os.getenv("BUCKET_NAME")

## Bedrock
from langchain_community.embeddings import BedrockEmbeddings

## Text Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

## Pdf Loader
from langchain_community.document_loaders import PyPDFLoader

## import FAISS
from langchain_community.vectorstores import FAISS

bedrock_client = boto3.client(service_name="bedrock-runtime", region_name='us-east-1')
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)

def get_unique_id():
    return str(uuid.uuid4())

## Split the pages / text into chunks
def split_text(pages, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(pages)
    return docs

## create vector store
def create_vector_store(request_id, documents):
    if not documents:
        st.write("No documents to process for vector store.")
        return False

    try:
        vectorstore_faiss = FAISS.from_documents(documents, bedrock_embeddings)
        file_name = f"{request_id}.bin"
        folder_path = "/tmp"
        os.makedirs(folder_path, exist_ok=True)
        vectorstore_faiss.save_local(index_name=file_name, folder_path=folder_path)

        ## upload to S3
        s3_client.upload_file(Filename=f"{folder_path}/{file_name}.faiss", Bucket=BUCKET_NAME, Key=f"{request_id}.faiss")
        s3_client.upload_file(Filename=f"{folder_path}/{file_name}.pkl", Bucket=BUCKET_NAME, Key=f"{request_id}.pkl")

        return True
    except Exception as e:
        st.write(f"Error creating vector store: {e}")
        return False

## main method
def main():
    st.write("Administrator Home Page...")
    uploaded_files = st.file_uploader("Choose files", type="pdf", accept_multiple_files=True)
    if uploaded_files is not None:
        all_splitted_docs = []
        for uploaded_file in uploaded_files:
            request_id = get_unique_id()
            st.write(f"Processing file with Request Id: {request_id}")
            saved_file_name = f"{request_id}.pdf"
            with open(saved_file_name, mode="wb") as w:
                w.write(uploaded_file.getvalue())

            loader = PyPDFLoader(saved_file_name)
            pages = loader.load_and_split()

            st.write(f"Total Pages in {request_id}: {len(pages)}")

            ## Split Text
            splitted_docs = split_text(pages, 1000, 200)
            if not splitted_docs:
                st.write(f"No text found in file {request_id}")
                continue

            st.write(f"Splitted Docs length for {request_id}: {len(splitted_docs)}")
            st.write("===================")
            st.write(splitted_docs[0])
            st.write("===================")
            st.write(splitted_docs[1])

            all_splitted_docs.extend(splitted_docs)

        if all_splitted_docs:
            st.write("Creating the Vector Store for all uploaded files")
            final_request_id = get_unique_id()
            result = create_vector_store(final_request_id, all_splitted_docs)

            if result:
                st.write(f"Hurray!! All PDFs processed successfully into Vector Store with Request Id: {final_request_id}")
            else:
                st.write("Error processing PDFs!! Please check logs.")
        else:
            st.write("No valid documents found to create a vector store.")

if __name__ == "__main__":
    main()
