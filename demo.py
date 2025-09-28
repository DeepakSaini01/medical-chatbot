# from flask import Flask, render_template,jsonify,request
# from src.helper import download_hugging_face_embedding
# from pinecone.grpc import PineconeGRPC as Pinecone
# from pinecone import ServerlessSpec
# from langchain_pinecone import PineconeVectorStore
# from langchain.prompts import PromptTemplate
# from langchain_community.llms import CTransformers
# from langchain.chains import RetrievalQA
# from src.prompt import *
# from dotenv import load_dotenv
# import os


# app=Flask(__name__)

# load_dotenv()
# PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")

# embeddings=download_hugging_face_embedding()


# pc = Pinecone(api_key=PINECONE_API_KEY)
# index_name="medicalbot"

# docsearch = PineconeVectorStore.from_existing_index(
#     index_name=index_name,
#     embedding=embeddings
# )


# PROMPT = PromptTemplate(
#     template=prompt_template,
#     input_variables=["context", "question"]
# )


# llm = CTransformers(
#     model="model/llama-2-7b-chat.ggmlv3.q2_K.bin",
#     model_type="llama",
#     config={
#         'max_new_tokens': 512,
#         'temperature': 0.8
#     }
# )


# qa=RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=docsearch.as_retriever(search_kwargs={'k': 1}),
#     return_source_documents=True,
#     chain_type_kwargs={"prompt": PROMPT} 
   
# )


# @app.route("/")
# def index():
#     return render_template('chat.html')

# @app.route("/get", methods=["GET", "POST"])
# def chat():
#     msg = request.form["msg"]
#     result = qa.invoke({"query": msg})
#     response_text = result["result"]
#     print("Response:", response_text)
#     return jsonify({"response": response_text}) 

# if __name__== '__main__':
#     app.run(host="0.0.0.0",port=8080,debug=True)



