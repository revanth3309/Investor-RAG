import shutil
#from fastapi import APIRouter, File, UploadFile
from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import os
from langchain_openai import AzureOpenAIEmbeddings
from vectorstore.azure_ai_search import AzureAISearchVectorStore
from ingestion.ingest_documents import ingest_document
from database.postgres_sql import (
    report_exists,
    delete_metrics
)

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

@router.delete("/documents")
async def delete_document(
    company: str,
    year: int
):
    """
    Delete a financial report from:

    1. Azure AI Search
    2. PostgreSQL
    3. Local PDF/Markdown files
    """

    company = company.strip()

    if not company:
        raise HTTPException(
            status_code=400,
            detail="Company name cannot be empty."
        )

    try:
        # Initialize Azure AI Search vector store
        vector_store = AzureAISearchVectorStore(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            api_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
        )

        # 1. Delete chunks + embeddings from Azure AI Search
        deleted_chunks = vector_store.delete_by_document(
            company=company,
            year=str(year)
        )

        # 2. Delete KPI records from PostgreSQL
        deleted_metrics = delete_metrics(
            company=company,
            year=year
        )

        # Expected PDF filename
        source_file = f"{year}_{company}.pdf"

        # 3. Delete PDF from local storage
        pdf_path = Path("data/raw_pdfs") / source_file

        pdf_deleted = False

        if pdf_path.exists():
            pdf_path.unlink()
            pdf_deleted = True

        # 4. Delete generated Markdown
        markdown_path = (
            Path("data/markdown")
            / f"{Path(source_file).stem}.md"
        )

        markdown_deleted = False

        if markdown_path.exists():
            markdown_path.unlink()
            markdown_deleted = True

        return {
            "message": "Document deleted successfully",
            "company": company,
            "year": year,
            "source_file": source_file,
            "deleted_vector_chunks": deleted_chunks,
            "deleted_metrics": deleted_metrics,
            "deleted_pdf": pdf_deleted,
            "deleted_markdown": markdown_deleted
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )