from Bio import Entrez
import pandas as pd
import time
from tqdm import tqdm   # progress bar

# Configure Entrez
Entrez.email = "aggarwalashutosh2006@gmail.com"
Entrez.api_key = "7dba9e25bd9d77d187d8afba01c640bd2d09"
query = '("Arsenic") AND ("Prenatal") AND ("Humans")'

# Step 1: Get total results
handle = Entrez.esearch(db="pubmed", term=query, retmax=1)
record = Entrez.read(handle)
handle.close()

total = int(record["Count"])
print(f"Total results found: {total}")

# Step 2: Fetch ALL PMIDs (in batches)
pmids = []
step = 200
for start in range(0, total, step):
    handle = Entrez.esearch(db="pubmed", term=query, retstart=start, retmax=step)
    rec = Entrez.read(handle)
    handle.close()
    pmids.extend(rec["IdList"])
    time.sleep(0.3)

print(f"Collected {len(pmids)} PMIDs ✅")

# Step 3: Batch fetch details with QC checks
papers = []
batch_size = 100   # fetch 100 papers at once

for i in tqdm(range(0, len(pmids), batch_size), desc="Fetching papers"):
    batch_pmids = pmids[i:i+batch_size]
    try:
        fetch = Entrez.efetch(db="pubmed", id=",".join(batch_pmids), rettype="medline", retmode="xml")
        data = Entrez.read(fetch)
        fetch.close()
        
        for article_record in data.get("PubmedArticle", []):
            citation = article_record.get("MedlineCitation", {})
            article = citation.get("Article", {})
            
            pmid = citation.get("PMID", "")
            title = article.get("ArticleTitle", "").strip()
            
            # Handle abstract safely
            abstract_parts = article.get("Abstract", {}).get("AbstractText", [])
            abstract = " ".join(abstract_parts).strip() if isinstance(abstract_parts, list) else str(abstract_parts)
            
            journal = article.get("Journal", {}).get("Title", "").strip()
            year = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {}).get("Year", "")
            
            # QC checks
            if not pmid:
                print(f"⚠️ Missing PMID in batch {i}")
                continue
            if not title:
                title = "[NO TITLE FOUND]"
            if not abstract:
                abstract = "[NO ABSTRACT FOUND]"
            if not year.isdigit():
                year = "[NO YEAR FOUND]"
            
            papers.append([pmid, title, abstract, journal, year])

    except Exception as e:
        print(f"❌ Error fetching batch starting at {i}: {e}")

    # Save partial CSV every 500 papers (checkpoint)
    if i % 500 == 0 and papers:
        df = pd.DataFrame(papers, columns=["PMID", "Title", "Abstract", "Journal", "Year"])
        df.drop_duplicates(subset=["PMID"], inplace=True)
        df.to_csv("toxicant_dohad_papers_partial.csv", index=False, encoding="utf-8")

# Step 4: Save final CSV
df = pd.DataFrame(papers, columns=["PMID", "Title", "Abstract", "Journal", "Year"])
df.drop_duplicates(subset=["PMID"], inplace=True)

# Final QC checks
missing_titles = df[df["Title"] == "[NO TITLE FOUND]"].shape[0]
missing_abstracts = df[df["Abstract"] == "[NO ABSTRACT FOUND]"].shape[0]
missing_years = df[df["Year"] == "[NO YEAR FOUND]"].shape[0]

print(f"\n📊 QC Report:")
print(f"   Total papers collected: {len(df)}")
print(f"   Missing titles: {missing_titles}")
print(f"   Missing abstracts: {missing_abstracts}")
print(f"   Missing years: {missing_years}")

df.to_csv("toxicant_dohad_papers_clean.csv", index=False, encoding="utf-8")
print(f"\n✅ Saved final CSV with {len(df)} papers")
