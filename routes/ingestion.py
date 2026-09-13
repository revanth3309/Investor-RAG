import shutil
#from fastapi import APIRouter, File, UploadFile
from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import os
from langchain_openai import AzureOpenAIEmbeddings
from vectorstore.azure_ai_search import AzureAISearchVectorStore
from ingestion.ingest_documents import ingest_document
from database.postgres_sql import report_exists

router = APIRouter()


"""@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    upload_dir = Path("data/raw_pdfs")
    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

        # Initialize embeddings and vector store
        embeddings = AzureOpenAIEmbeddings(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )

        vector_store = AzureAISearchVectorStore(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            api_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
        )

        ingest_document(
            pdf_path=str(file_path),
            embeddings=embeddings,
            vector_store=vector_store
        )

    return {
        "message": "Document uploaded successfully",
        "file_name": file.filename
    }"""


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="File name is missing."
        )

    # Extract company and year from filename
    file_stem = Path(filename).stem

    try:
        year_str, company = file_stem.split("_", 1)
        year = int(year_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid file name format. Expected: year_company.pdf"
    )

    company = company.strip()

    if not company:
        raise HTTPException(
        status_code=400,
        detail="Company name cannot be empty."
    )

    # Check if report already exists
    if report_exists(company, year):
        raise HTTPException(
            status_code=409,
            detail=f"{company}_{year} already exists."
        )

    # Save uploaded PDF
    upload_dir = Path("data/raw_pdfs")
    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Initialize embeddings and vector store
    embeddings = AzureOpenAIEmbeddings(
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

    vector_store = AzureAISearchVectorStore(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        api_key=os.getenv("AZURE_SEARCH_API_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
    )

    # Existing ingestion pipeline
    ingest_document(
        pdf_path=str(file_path),
        embeddings=embeddings,
        vector_store=vector_store
    )

    return {
        "message": "Document uploaded successfully",
        "file_name": filename,
        "company": company,
        "year": year
    }