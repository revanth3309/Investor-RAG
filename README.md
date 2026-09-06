# AI-Powered Investor Intelligence Platform

This repository contains the Python backend for an AI-powered Investor Intelligence Platform, including document ingestion, semantic search, KPI extraction, Azure AI Search integration, Azure OpenAI integration, and PostgreSQL-based KPI storage.

## Prerequisites

- Python 3.12+
- UV Package Manager

## Setup

### 1. Install UV

#### Windows

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```

---

### 2. Create Virtual Environment

```bash
uv venv
```

---

### 3. Activate Virtual Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### macOS/Linux

```bash
source .venv/bin/activate
```

---

### 4. Install Dependencies

```bash
uv pip install -r requirements.txt
```

---

### 5. Configure Environment Variables

Create a `.env` file in the project root and configure all required environment variables before running the application.

The required configuration includes:

- Azure OpenAI credentials and endpoints
- Azure AI Search credentials and endpoints
- PostgreSQL database credentials and connection details

> **Note:** Never commit the `.env` file or expose API keys, passwords, or other secrets in source control.

---

### 6. Run the Application

```bash
python app.py
```

---

## Project Features

- Annual Report Upload & Processing
- KPI Extraction using Azure OpenAI
- Azure AI Search Integration
- Semantic Search & Retrieval
- RAG-based Chatbot
- PostgreSQL KPI Storage
- Investor Insights Dashboard
- Production-Grade Modular Architecture

---

## Technology Stack

### Backend

- FastAPI
- Python 3.12

### AI Services

- Azure OpenAI
- Azure AI Search

### Database

- Azure PostgreSQL

### Deployment

- Docker
- Azure Container Registry (ACR)
- Azure Kubernetes Service (AKS)

### Package Management

- UV

---

## High-Level Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │       Backend       │
                         └──────────┬──────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
       ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
       │ Annual Reports │  │  Azure OpenAI  │  │ Azure AI Search│
       │   Processing   │  │                │  │                │
       └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
               │                   │                   │
               │                   ▼                   │
               │          ┌────────────────┐           │
               │          │  KPI Extraction│           │
               │          └───────┬────────┘           │
               │                  │                    │
               └──────────────────┼────────────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Semantic Search &   │
                       │      Retrieval      │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    RAG Chatbot &    │
                       │ Investor Insights   │
                       └──────────┬──────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           ┌─────────────────┐        ┌──────────────────┐
           │   PostgreSQL    │        │ Investor Insights│
           │   KPI Storage   │        │    Dashboard     │
           └─────────────────┘        └──────────────────┘
```

---

## Project Structure

```text
AI-Powered-Investor-Intelligence-Platform/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
├── ...
│
└── ...
```

---

## Getting Started

Follow these steps to get the application running locally:

1. Install Python 3.12+.
2. Install UV Package Manager.
3. Create a virtual environment using `uv venv`.
4. Activate the virtual environment.
5. Install dependencies using `uv pip install -r requirements.txt`.
6. Create and configure the `.env` file.
7. Configure the required Azure resources.
8. Configure PostgreSQL and ensure the database is accessible.
9. Run the application using `python app.py`.

---

## Notes

- Ensure all Azure resources are configured before running the application.
- Verify that PostgreSQL firewall rules allow access from the application.
- Ensure the required Azure OpenAI deployments are available.
- Ensure the required Azure AI Search services and indexes are configured.
- Store secrets in environment variables and never commit `.env` files to source control.
- For production deployments, use Azure Key Vault or Kubernetes Secrets for secret management.

---

## Security

This project uses credentials for Azure AI services and PostgreSQL database access.

Follow these security practices:

- Never commit API keys or passwords.
- Add `.env` to `.gitignore`.
- Use environment variables for local development.
- Do not hard-code secrets in Python source files.
- Use Azure Key Vault or Kubernetes Secrets for production deployments.
- Rotate credentials immediately if they are accidentally exposed.

---

## Deployment

The application can be containerized using Docker and deployed to Azure infrastructure.

The recommended deployment stack includes:

- Docker for containerization
- Azure Container Registry (ACR) for storing container images
- Azure Kubernetes Service (AKS) for container orchestration
- Azure Key Vault or Kubernetes Secrets for secure configuration

---

## License

Add the appropriate project license here if the repository is intended to be distributed publicly.
