# ================================================================
# 🛡️ AWS Security & Compliance Chatbot
# (Amazon Bedrock + ChatGPT + LangChain + Streamlit)
# ================================================================

import streamlit as st
import boto3
import os
from pathlib import Path
from langchain_aws.chat_models import ChatBedrock
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_chroma import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------------------------------------------
# 1️⃣ Environment Setup
# ---------------------------------------------------------------
load_dotenv()  # loads .env if exists

# Required: OPENAI_API_KEY=sk-xxxxx
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    st.warning("⚠️ Missing OpenAI API key. Please add it to your .env file.")
client = OpenAI(api_key=openai_key)

# ---------------------------------------------------------------
# 2️⃣ AWS & Model Setup
# ---------------------------------------------------------------
boto3_session = boto3.session.Session()
region = boto3_session.region_name or "us-east-1"

model_id = "amazon.titan-text-lite-v1"
embedding_model = "amazon.titan-embed-text-v1"
temperature = 0.2

# Initialize Bedrock model
llm_chat = ChatBedrock(
    model_id=model_id,
    model_kwargs={"temperature": temperature},
    region_name=region
)

embedding = BedrockEmbeddings(
    model_id=embedding_model,
    region_name=region
)

# ---------------------------------------------------------------
# 3️⃣ Chroma Vector Store (persistent knowledge)
# ---------------------------------------------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
INDEX_DIR = "security_index"

nist_file = DATA_DIR / "nist_800-53_summary.txt"
cis_file = DATA_DIR / "cis_rhel_benchmark.txt"

# Default context if missing
if not nist_file.exists():
    nist_file.write_text("""
NIST 800-53 AC-2: Manage IAM users/roles and enforce least privilege using AWS IAM policies.
Use AWS Config rules for periodic review of permissions and access keys.
CM-2: Maintain baseline configurations using Systems Manager and AWS Config Conformance Packs.
""")

if not cis_file.exists():
    cis_file.write_text("""
CIS Linux hardening: Disable root SSH, enforce password complexity, enable auditd,
restrict firewall rules, and regularly patch instances with AWS Systems Manager.
""")

def build_or_load_index():
    if Path(INDEX_DIR).exists():
        print("✅ Loading existing Chroma index...")
        return Chroma(persist_directory=INDEX_DIR, embedding_function=embedding)
    print("⚙️ Building Chroma index from ./data ...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = []
    for file in DATA_DIR.glob("*.txt"):
        docs += splitter.split_documents(TextLoader(str(file)).load())
    vectorstore = Chroma.from_documents(docs, embedding, persist_directory=INDEX_DIR)
    vectorstore.persist()
    print("💾 Index saved to", INDEX_DIR)
    return vectorstore

vectorstore = build_or_load_index()
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# ---------------------------------------------------------------
# 4️⃣ Memory
# ---------------------------------------------------------------
store = {}
def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

with_message_history = RunnableWithMessageHistory(llm_chat, get_session_history)

# ---------------------------------------------------------------
# 5️⃣ Context for Security & Compliance
# ---------------------------------------------------------------
SECURITY_CONTEXT = """
You are an AWS Security & Compliance expert.
Explain cybersecurity and compliance frameworks (FISMA, NIST 800-53, CIS, FedRAMP)
and how to implement them using AWS services such as IAM, Config, GuardDuty,
SecurityHub, CloudTrail, and CloudWatch.
Be concise and provide AWS service mapping examples when possible.
"""

# ---------------------------------------------------------------
# 6️⃣ Chat Functions
# ---------------------------------------------------------------
def ask_bedrock(question: str, session_id="sec-bot-ui"):
    """Try answering using Amazon Bedrock Titan."""
    ctx_docs = retriever.invoke(question)
    ctx = "\n\n".join([d.page_content for d in ctx_docs]) if ctx_docs else ""
    prompt = f"""{SECURITY_CONTEXT}

Context:
{ctx}

Question: {question}
"""
    response = with_message_history.invoke(
        [HumanMessage(content=prompt)],
        config={"configurable": {"session_id": session_id}},
    )
    return response.content

def ask_chatgpt(question: str):
    """Fallback to OpenAI GPT when Bedrock can't respond."""
    prompt = f"{SECURITY_CONTEXT}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SECURITY_CONTEXT},
                  {"role": "user", "content": question}],
        max_tokens=500,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def ask_secure_bot(question: str, session_id="sec-bot-ui"):
    """Try Bedrock first, then fallback to ChatGPT."""
    try:
        answer = ask_bedrock(question, session_id)
        if "unable to respond" in answer.lower() or not answer.strip():
            raise Exception("Bedrock failed, switching to ChatGPT")
        return f"🧠 **Bedrock:**\n\n{answer}"
    except Exception as e:
        print(f"[Fallback] {e}")
        try:
            gpt_answer = ask_chatgpt(question)
            return f"🤖 **ChatGPT Fallback:**\n\n{gpt_answer}"
        except Exception as e2:
            return f"❌ Both models failed: {e2}"

# ---------------------------------------------------------------
# 7️⃣ Streamlit UI
# ---------------------------------------------------------------
st.set_page_config(page_title="AWS Security & Compliance Chatbot", page_icon="🛡️")
st.title("🛡️ AWS Security & Compliance Chatbot")
st.caption("Powered by Amazon Bedrock + OpenAI + LangChain")

user_question = st.text_input("Ask a compliance or security question:")

if st.button("Ask") and user_question:
    with st.spinner("Analyzing with Bedrock..."):
        try:
            answer = ask_secure_bot(user_question)
            st.markdown(answer)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
