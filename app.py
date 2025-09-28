
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, render_template,jsonify,request
from src.helper import download_hugging_face_embedding
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA
from src.prompt import *
from dotenv import load_dotenv
import os

import threading
from twilio.rest import Client

app = Flask(__name__)

load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER") 

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

try:
    embeddings = download_hugging_face_embedding()
except ModuleNotFoundError as e:
    print("Error loading embeddings:", e)
    embeddings = None

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medicalbot"

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

llm = CTransformers(
    model="model/llama-2-7b-chat.ggmlv3.q2_K.bin",
    model_type="llama",
    config={'max_new_tokens': 512, 'temperature': 0.8}
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever(search_kwargs={'k': 1}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

@app.route("/whatsapp", methods=["POST", "GET"])
def whatsapp_bot():
    if request.method == "GET":
        return "WhatsApp webhook running. Send a POST request from Twilio."

    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From")  
    print("Incoming WhatsApp message:", incoming_msg)
    # print("From number:", from_number)

    resp = MessagingResponse()

    if incoming_msg:
        
        resp.message("⚡ Got your message! Let me think...")
        print("Placeholder sent")

        
        def process_qa(msg, to_number):
            try:
                result = qa.invoke({"query": msg})
                answer = result["result"]
                print("QA Result:", answer)

                try:
                    message = client.messages.create(
                        body=answer,
                        from_=TWILIO_WHATSAPP_NUMBER,
                        to=to_number
                    )
                    print("QA answer sent. SID:", message.sid)
                except Exception as e:
                    print("Error sending WhatsApp message via Twilio:", e)

            except Exception as e:
                print("Error in QA processing:", e)

        threading.Thread(target=process_qa, args=(incoming_msg, from_number)).start()

    else:
        resp.message("Hi 👋, I'm your Medical Assistant bot. Please ask a question.")
        print("Bot reply:", "Hi 👋, I'm your Medical Assistant bot.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
