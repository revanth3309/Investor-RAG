import os
from types import SimpleNamespace

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, Field

from llm.azure_openai import get_structured_completion
from vectorstore.azure_ai_search import AzureAISearchVectorStore

load_dotenv()


class FinancialMetrics(BaseModel):
    revenue: str | int | None = None
    net_income: str | int | None = None
    operating_income: str | int | None = None
    cash_flow_from_operating_activities: str | int | None = None
    total_assets: str | int | None = None
    total_liabilities: str | int | None = None
    top_risk_factors: list[str] | None = None
    top_growth_drivers: list[str] | None = None


class Retriever:
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

    For KPI extraction, we retrieve all available chunks
    belonging to the requested company and year.
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

        if content.strip():
            documents.append(
                SimpleNamespace(
                    page_content=content
                )
            )

    print(
         f"[KPI DEBUG] Retrieved {len(documents)} "
         f"chunks for {company} {year}"
    )

    return documents

def retrieve_context(
    retriever: Retriever,
    company: str,
    year: int
) -> str:
    """
    Retrieve all available financial context for a company/year.
    """

    documents = retriever.invoke(
        query="*",
        company=company,
        year=year,
        top_k=100
    )

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    print(
        f"[KPI DEBUG] Context length: {len(context)} characters"
    )

    return context


def build_extraction_prompt(
    company: str,
    year: int,
    context: str
) -> str:
    """
    Build KPI extraction prompt.
    """

    return f"""
You are an expert financial analyst extracting data from
an annual financial report.

Company: {company}
Fiscal Year: {year}

You must extract the requested information ONLY from the
provided report context.

================ REPORT CONTEXT ================

{context}

================ END REPORT CONTEXT ================

Extract:

1. Revenue
2. Net Income
3. Operating Income
4. Cash Flow from Operating Activities
5. Total Assets
6. Total Liabilities
7. Top Risk Factors
8. Top Growth Drivers

IMPORTANT INSTRUCTIONS:

- Search the ENTIRE provided context before deciding that a
  value is unavailable.
- Financial values must be copied exactly as reported.
- Preserve currency symbols and units when they are present.
- Do not calculate or estimate values.
- Do not use outside knowledge.
- Revenue should come from the company's income statement
  or consolidated statements of operations.
- Net Income should come from the income statement.
- Operating Income should come from the income statement
  when explicitly reported.
- Cash Flow from Operating Activities should come from the
  cash flow statement.
- Total Assets and Total Liabilities should come from the
  balance sheet.
- Identify the most important risks explicitly discussed
  in the report.
- Identify the most important growth drivers explicitly
  discussed in the report.
- Return null only when the requested information genuinely
  does not appear anywhere in the provided context.
- Return valid structured JSON only.
"""


def extract_financial_metrics(
    retriever: Retriever,
    company: str,
    year: int
) -> dict:
    """
    Extract KPIs using RAG.
    """

    context = retrieve_context(
        retriever=retriever,
        company=company,
        year=year
    )

    if not context.strip():
        raise ValueError(
            f"No context retrieved for {company} {year}. "
            "KPI extraction cannot continue."
        )

    print(
        f"[KPI DEBUG] Sending {len(context)} "
        f"characters of context to the LLM."
    )

    print("\n" + "=" * 80)
    print("[KPI DEBUG] CONTEXT SENT TO LLM")
    print("=" * 80)
    print(context[:10000])
    print("=" * 80)

    prompt = build_extraction_prompt(
        company=company,
        year=year,
        context=context
    )

    metrics = get_structured_completion(
        prompt=prompt,
        response_model=FinancialMetrics
    )

    print("\n[debug] Structured parsed output:")
    print(metrics)

    return metrics.model_dump()


def main() -> None:
    company = "Apple"
    year = 2024

    vector_store = AzureAISearchVectorStore(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        api_key=os.getenv("AZURE_SEARCH_API_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
    )

    retriever = Retriever(
        vector_store.client
    )

    results = extract_financial_metrics(
        retriever=retriever,
        company=company,
        year=year
    )

    print(f"\nExtracted KPIs for {company} {year}\n")

    for key, value in results.items():
        print(f"{key}:")
        print(value)
        print("-" * 80)


    from database.save_metrics import save_metrics

    save_metrics(
        company=company,
        year=year,
        metrics=results
    )

if __name__ == "__main__":
    main()