import boto3
import streamlit as st
import os
import uuid
import webbrowser

## s3_client
s3_client = boto3.client("s3")
BUCKET_NAME = os.getenv("BUCKET_NAME")

## Bedrock
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

## prompt and chain
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

## Text Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

## Pdf Loader
from langchain_community.document_loaders import PyPDFLoader

## import FAISS
from langchain_community.vectorstores import FAISS

bedrock_client = boto3.client(service_name="bedrock-runtime")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)

folder_path = "/tmp/"

def get_unique_id():
    return str(uuid.uuid4())

## load index
def load_index():
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    faiss_files = []
    pkl_files = []

    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith(".faiss"):
            faiss_files.append(key)
        elif key.endswith(".pkl"):
            pkl_files.append(key)

    if not faiss_files or not pkl_files:
        raise FileNotFoundError("Required FAISS or PKL file not found in the bucket.")

    faiss_local_paths = []
    pkl_local_paths = []

    for faiss_file in faiss_files:
        faiss_local_path = os.path.join(folder_path, faiss_file.split('/')[-1])
        #st.write(f"Downloading {faiss_file} to {faiss_local_path}")
        s3_client.download_file(Bucket=BUCKET_NAME, Key=faiss_file, Filename=faiss_local_path)
        faiss_local_paths.append(faiss_local_path)

    for pkl_file in pkl_files:
        pkl_local_path = os.path.join(folder_path, pkl_file.split('/')[-1])
        #st.write(f"Downloading {pkl_file} to {pkl_local_path}")
        s3_client.download_file(Bucket=BUCKET_NAME, Key=pkl_file, Filename=pkl_local_path)
        pkl_local_paths.append(pkl_local_path)

    return faiss_local_paths, pkl_local_paths

def get_llm():
    llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client,
                  model_kwargs={'max_tokens_to_sample': 512})
    return llm

# get_response()
def get_response(llm, vectorstore, question):
    ## create prompt / template
    prompt_template = """
    Human: Please use the given context to provide concise answer to the question
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    <context>
    {context}
    </context>
    Question: {question}
    Assistant:"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    answer = qa({"query": question})
    return answer['result']

## main method
def main():
    st.header("Bedrock Chat: Explore PDFs with Conversational AI")

    st.write("To upload the documents please click [here](http://localhost:8083/)")

    faiss_local_paths, pkl_local_paths = load_index()

    dir_list = os.listdir(folder_path)
    #st.write(f"Files and Directories in {folder_path}")
    #st.write(dir_list)

    #st.write(f"FAISS file path: {faiss_local_paths}")
    #st.write(f"PKL file path: {pkl_local_paths}")

    ## create index
    faiss_indexes = []
    for faiss_local_path in faiss_local_paths:
        faiss_index = FAISS.load_local(
            index_name=faiss_local_path.split('/')[-1].replace('.faiss', ''),
            folder_path=folder_path,
            embeddings=bedrock_embeddings,
            allow_dangerous_deserialization=True
        )
        faiss_indexes.append(faiss_index)
    faiss_index = None
    for index in faiss_indexes:
        if faiss_index is None:
            faiss_index = index
        else:
            faiss_index.merge_from(index)
    

    st.write("PDFs are ready for the chat..")
    question = st.text_input("Please ask your question")
    if st.button("Submit"):
        with st.spinner("Querying..."):

            llm = get_llm()

            # get_response
            st.write(get_response(llm, faiss_index, question))
            st.success("Done")

if __name__ == "__main__":
    main()


#docker run -e BUCKET_NAME=bedrock-350474408512-us-east-1 -v C:\Users\manis\.aws:/root/.aws -p 8083:8083 -it pdf-reader-admin

#docker run -e BUCKET_NAME=bedrock-350474408512-us-east-1 -v C:\Users\manis\.aws:/root/.aws -p 8084:8084 -it pdf-reader-client

