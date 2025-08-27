import requests
import feedparser
import pandas as pd
from datetime import datetime    #For timestamp
import tkinter as tk        #For dialog box 
from tkinter import simpledialog #For dialog box

# --------------------------
# Fuction: Fetching data from semantic scholar API
# --------------------------
def fetch_semantic_scholar(query, limit=5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit, "fields": "title,abstract,authors,year,doi,url"}
    response = requests.get(url, params=params)
    papers = []
    #if response is OK
    if response.status_code == 200:
        for p in response.json().get("data", []):
            papers.append({
                "timestamp": datetime.now().isoformat(),
                "title": p.get("title"),
                "year": p.get("year"),
                "author": ", ".join([a["name"] for a in p.get("authors", [])]),
                "doi": p.get("doi"),
                "url": p.get("url"),
                "abstract": p.get("abstract")
            })
    return papers

# --------------------------
# Fuction: Fetching data from arxiv API
# --------------------------
def fetch_arxiv(query, limit=5):
    base_url = "http://export.arxiv.org/api/query"
    params = {"search_query": query, "start": 0, "max_results": limit}
    response = requests.get(base_url, params=params)
    feed = feedparser.parse(response.text)
    papers = []
    for entry in feed.entries:
        papers.append({
            "timestamp": datetime.now().isoformat(),
            "title": entry.title,
            "year": entry.published[:4],
            "author": ", ".join([a.name for a in entry.authors]),
            "doi": entry.get("arxiv_doi", "N/A"),
            "url": entry.link,
            "abstract": entry.summary
        })
    return papers

# --------------------------
# Fuction: Fetching data from openAlex API
# --------------------------
def fetch_openalex(query, limit=5):
    url = "https://api.openalex.org/works"
    params = {"search": query, "per-page": limit}
    response = requests.get(url, params=params)
    papers = []
    #if response is OK
    if response.status_code == 200:
        for p in response.json().get("results", []):
            papers.append({
                "timestamp": datetime.now().isoformat(),
                "title": p.get("title"),
                "year": p.get("publication_year"),
                "author": ", ".join([a["author"]["display_name"] for a in p.get("authorships", [])]),
                "doi": p.get("doi"),
                "url": p.get("id"),
                "abstract": p.get("abstract", None)
            })
    return papers

# --------------------------
# Fuction: Fetching data from Crossref REST API
# --------------------------
def fetch_crossref(query, limit=5):
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": limit}
    response = requests.get(url, params=params)
    papers = []
    #if response is OK
    if response.status_code == 200:
        for p in response.json().get("message", {}).get("items", []):
            papers.append({
                "timestamp": datetime.now().isoformat(),
                "title": p.get("title", ["N/A"])[0],
                "year": p.get("issued", {}).get("date-parts", [[None]])[0][0],
                "author": ", ".join([f"{a.get('given', '')} {a.get('family', '')}" for a in p.get("author", [])]) if "author" in p else "N/A",
                "doi": p.get("DOI"),
                "url": p.get("URL"),
                "abstract": p.get("abstract", "N/A")
            })
    return papers

# --------------------------
# Function: Main Processing of the program 
# Limitation: Since AI APIs are expensive, I wasn’t able to integrate AI into this workflow.
# Recommendation: Include AI (e.g., OpenAI) to perform context analysis, summarization, and evaluation of strengths and weaknesses.
# --------------------------
def main():
    # GUI dialog box for user input
    root = tk.Tk()
    root.withdraw()
    query = simpledialog.askstring("Research Query", "Enter your research query:")
    max_results = simpledialog.askinteger("Max Results", "Enter max number of papers:", minvalue=1, maxvalue=50)

    # fetch datas from different Research Papers
    papers = []
    papers.extend(fetch_semantic_scholar(query, max_results))
    papers.extend(fetch_arxiv(query, max_results))
    papers.extend(fetch_openalex(query, max_results))
    papers.extend(fetch_crossref(query, max_results))


    # Save everything in excel in "xlsx" format.
    df = pd.DataFrame(papers)
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{query.replace(' ', '_')}_Papers_{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Results saved to {filename}")

if __name__ == "__main__":
    main()
