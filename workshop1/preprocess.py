# Bailey
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
def clean_and_tokenize(text: str) -> list[str]:
    #takes raw text and lowercases it + removes punctuation
    lowerCaseText = text.lower()
    text = re.sub(r'[^\w\s]','',text)
    tokens = text.split()
    return tokens

def lemmatize_terms(tokens: list[str]) -> list[str]:
    # Use WordNetLemmatizer to lemmatize terms.
    lemmatize = WordNetLemmatizer()
    lemmatizedTokens = []
    for token in tokens:
        base = lemmatize.lemmatize(token)
        lemmatizedTokens.append(base)
    return lemmatizedTokens
    

def remove_common_words(tokens: list[str]) -> list[str]:
    #take tokens and remove common words 
    stop = set(stopwords.words('english')
    outputTokens = []
    for token in tokens:
        if token not in stop:
            outputTokens.append(token)
    return outputTokens

def preprocess_text(text: str) -> list[str]:
    #return cleaned list of terms
    tokens = cleaned_and_tokenize(text)
    tokens = lemmatize_terms(tokens)
    tokens = remove_common_words(tokens)

    return tokens
    
