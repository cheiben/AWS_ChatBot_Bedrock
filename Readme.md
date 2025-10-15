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
```
<img width="1644" height="530" alt="image" src="https://github.com/user-attachments/assets/235cad2b-e523-4178-aed2-376910dc219b" />

---

# 🛡️ AWS Security & Compliance Chatbot

### *(Amazon Bedrock + ChatGPT + Streamlit + LangChain)*

This project is a **simple AI chatbot** that explains AWS security and compliance frameworks (FISMA, NIST 800-53, CIS, FedRAMP) and how they’re implemented in AWS services — powered by **Amazon Bedrock** and **OpenAI (ChatGPT)**.

---

## 🚀 Quick Setup (on AWS EC2)

### 1️⃣ Launch an EC2 instance

* Go to the **AWS Console → EC2 → Launch Instance**
* Use **Amazon Linux 2023**
* Instance type: `t3.medium` (you can use `t3.micro` for testing)
* Create IAM role with policy

``` {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```
* Allow inbound ports: `22` (SSH) and `8501` (Streamlit UI)

---

### 2️⃣ Connect to the instance

```bash
ssh -i my-key.pem ec2-user@<EC2_PUBLIC_IP>
```

---

### 3️⃣ Install dependencies

```bash
sudo yum update -y
sudo yum install -y git python3-pip
pip3 install --upgrade pip
```

Clone this repository:

```bash
https://github.com/cheiben/AWS_ChatBot_Bedrock.git
```

Install required Python packages:

```bash
pip install boto3 botocore awscli streamlit langchain langchain-aws langchain-community langchain-chroma chromadb openai python-dotenv
```

---

### 4️⃣ Add environment variables

Create a `.env` file:

```bash
nano .env
```

Add:

```bash
OPENAI_API_KEY=sk-your-openai-key-here
AWS_DEFAULT_REGION=us-east-1
```

> Save with `CTRL+O` then `CTRL+X`

---

### 5️⃣ Run the app

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

---

### 6️⃣ Open in your browser

Go to:

```
http://<EC2_PUBLIC_IP>:8501
```

You’ll see the chatbot UI where you can ask things like:

* “Explain NIST 800-53 AC-2 for AWS IAM.”
* “List CIS hardening steps for Red Hat EC2.”
* “Compare FISMA and FedRAMP requirements.”

---

## 🧠 How It Works

* **Amazon Bedrock (Titan)** answers AWS-specific compliance questions.
* **ChatGPT (OpenAI)** automatically takes over if Bedrock can’t respond.
* **ChromaDB** stores reference texts (NIST, CIS, etc.).
* **Streamlit** provides the interactive UI.

---

## 🪪 Folder Structure

```
AWS_ChatBot_Bedrock/
│
├── app.py                # Main chatbot app
├── data/                 # Local compliance text data
├── security_index/       # Chroma vector index (auto-created)
├── .env.example          # Example environment variables
├── requirements.txt      # Dependency list
└── README.md             # Setup guide
```

---

## 💸 Cost Tips

| Service                   | Cost                        |
| ------------------------- | --------------------------- |
| EC2 t3.micro              | ~$7/mo (free tier eligible) |
| Amazon Bedrock Titan Lite | ~$0.0004/request            |
| OpenAI ChatGPT            | ~$0.01/10 prompts           |
| Streamlit & Chroma        | Free (local)                |

👉 **Stop your EC2 instance** when not in use to avoid charges.

