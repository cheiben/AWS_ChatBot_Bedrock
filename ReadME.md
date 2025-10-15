# 🧠 AWS Security & Compliance Chatbot (Amazon Bedrock + ChatGPT + LangChain)

An intelligent chatbot built using **Amazon Bedrock**, **LangChain**, and **Streamlit** that explains and implements **AWS Security & Compliance frameworks** such as **FISMA**, **FedRAMP**, **NIST 800-53**, and **CIS Benchmarks**.

It can be deployed in AWS SageMaker, EC2, or locally via Streamlit.

---

## 🚀 Features

✅ Built on **Amazon Bedrock (Titan)** using LangChain  
✅ Integrated **ChatGPT (OpenAI)** fallback for broader reasoning  
✅ Persistent **Chroma vectorstore** for context-aware responses  
✅ Streamlit web UI for interactive Q&A  
✅ Deployable in **EC2** (t3.micro) or **SageMaker Notebook**  
✅ Extendable with new documents or frameworks  

---

## 🏗️ Architecture Overview

```text
User → Streamlit UI → Router
       ├──> Amazon Titan (Bedrock)
       └──> ChatGPT (OpenAI)
             ↑
        Chroma Vectorstore ← Compliance Docs (.txt / .pdf)
