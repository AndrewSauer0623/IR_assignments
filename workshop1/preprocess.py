# Bailey
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
def clean_and_tokenize(text: str) -> list[str]:
    #takes raw text and lowercases it + removes punctuation
    cleanText = text.lower()
    cleanText = re.sub(r'[^\w\s]','',cleanText)
    tokens = cleanText.split()
    return tokens

def lemmatize_terms(tokens: list[str]) -> list[str]:
    #use WordNetLemmatizer to lemmatize terms.
    lemmatizer = WordNetLemmatizer()
    lemmatizedTokens = []
    for token in tokens:
        base = lemmatizer.lemmatize(token)
        lemmatizedTokens.append(base)
    return lemmatizedTokens
    

def remove_common_words(tokens: list[str]) -> list[str]:
    #take tokens and remove common words 
    stop = set(stopwords.words('english'))
    outputTokens = []
    for token in tokens:
        if token not in stop:
            outputTokens.append(token)
    return outputTokens

def preprocess_text(text: str) -> list[str]:
    #return cleaned list of terms
    tokens = clean_and_tokenize(text)
    tokens = lemmatize_terms(tokens)
    tokens = remove_common_words(tokens)

    return tokens
    
def compute_term_frequencies(tokens_by_doc):
    """
    Input:  {doc_id: [tokens]}
    Output: {doc_id: {term: tf}}
    Count occurrences of each term per doc.
    """
    pass
