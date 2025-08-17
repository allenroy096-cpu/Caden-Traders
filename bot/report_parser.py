import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

# PDF parsing
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# NLP summarization (using transformers)
try:
    from transformers import pipeline
    summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
except Exception:
    summarizer = None

def parse_pdf_report(pdf_path):
    if not PyPDF2:
        raise ImportError('PyPDF2 is required for PDF parsing')
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def parse_html_report(url):
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Extract all text
    return soup.get_text(separator=' ', strip=True)

def extract_financial_tables(text):
    # Simple regex-based extraction for demo (customize for real use)
    tables = re.findall(r'(Revenue|Profit|EPS|Net Income|EBITDA)[^\n]+', text, re.IGNORECASE)
    return tables

def summarize_text(text, max_length=200):
    if summarizer:
        try:
            summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        except Exception:
            pass
    # Fallback: return first N words
    return ' '.join(text.split()[:max_length])

# Example usage:
# text = parse_pdf_report('annual_report.pdf')
# summary = summarize_text(text)
# tables = extract_financial_tables(text)
