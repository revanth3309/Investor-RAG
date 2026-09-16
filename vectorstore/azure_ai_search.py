import uuid

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from types import SimpleNamespace


class AzureAISearchVectorStore:
    """Azure AI Search vector store."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        index_name: str
    ) -> None:
        self.client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )

    def upload_chunks(
        self,
        chunks,
        embeddings,
        company: str,
        year: str,
        source_file: str
    ) -> None:
        """
        Upload chunks to Azure AI Search.
        """
        documents = []

        for chunk in chunks:
            vector = embeddings.embed_query(chunk.page_content)

            documents.append(
                {
                    "id": str(uuid.uuid4()),
                    "company": company,
                    "year": year,
                    "source_file": source_file,
                    "content": chunk.page_content,
                    "content_vector": vector
                }
            )

        result = self.client.upload_documents(documents)

        uploaded = sum(item.succeeded for item in result)

        print(f"Uploaded {uploaded}/{len(documents)} chunks.")

        for item in result:
           if not item.succeeded:
             print(
            f"[AZURE SEARCH ERROR] "
            f"Document key={item.key}, "
            f"status={item.status_code}, "
            f"error={item.error_message}"
        )

    def delete_by_document(
        self,
        company: str,
        year: str
    ) -> int:
        """
        Delete all Azure AI Search chunks belonging to a document.

        A document is identified by company + year.
        Returns the number of chunks deleted.
        """

        filter_expr = (
            f"company eq '{company}' "
            f"and year eq '{year}'"
        )

        results = self.client.search(
            search_text="*",
            filter=filter_expr,
            select=["id"]
        )

        document_ids = [
            {"id": result["id"]}
            for result in results
        ]

        if not document_ids:
            print(
                f"No Azure Search documents found for "
                f"{company} {year}."
            )
            return 0

        result = self.client.delete_documents(
            documents=document_ids
        )

        deleted = sum(
            item.succeeded
            for item in result
        )

        print(
            f"Deleted {deleted}/{len(document_ids)} "
            f"Azure Search chunks for {company} {year}."
        )

        return deleted

class Retriever:
    """
    Wrapper around Azure AI Search for retrieving document chunks.
    """

    def __init__(self, client):
        self.client = client

    def invoke(
        self,
        query: str,
        company: str | None = None,
        year: int | None = None,
        top_k: int = 100
    ) -> list:
        """
        Retrieve chunks from Azure AI Search.

        When company and year are provided, retrieve chunks
        belonging to that specific report.
        """

        filter_expr = None

        if company and year:
            filter_expr = (
                f"company eq '{company}' "
                f"and year eq '{year}'"
            )

        results = self.client.search(
            search_text="*",
            top=top_k,
            filter=filter_expr
        )

        documents = []

        for result in results:
            content = result.get("content", "")

            if content and content.strip():
                documents.append(
                    SimpleNamespace(
                        page_content=content
                    )
                )

        print(
            f"[RETRIEVER DEBUG] Retrieved "
            f"{len(documents)} chunks for "
            f"{company} {year}"
        )

        return documents