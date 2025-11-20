from typing import List, Optional
import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK data if not already
nltk.download('punkt_tab')
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)  # for WordNet

STOPWORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    return word_tokenize(text)

def remove_stopwords(tokens: List[str]) -> List[str]:
    return [tok for tok in tokens if tok not in STOPWORDS]

def lemmatize_tokens(tokens: List[str]) -> List[str]:
    return [lemmatizer.lemmatize(tok) for tok in tokens]

def expand_synonyms(tokens: List[str], max_synonyms_per_token: int = 2) -> List[str]:
    expanded: List[str] = []
    for tok in tokens:
        expanded.append(tok)
        syns = wordnet.synsets(tok)
        count = 0
        for syn in syns:
            for lemma in syn.lemmas():
                synonym = lemma.name().replace("_", " ")
                if synonym != tok and count < max_synonyms_per_token:
                    expanded.append(synonym)
                    count += 1
            if count >= max_synonyms_per_token:
                break
    return expanded

def preprocess_query(narrative: str, use_synonyms: bool = True) -> str:
    text = clean_text(narrative)
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize_tokens(tokens)
    if use_synonyms:
        tokens = expand_synonyms(tokens)
    return " ".join(tokens)
