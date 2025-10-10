# Bailey
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
def clean_and_tokenize(text: str) -> list[str]:
    """
    Input:  raw document text
    Output: list of lowercase tokens with punctuation removed
    """

def lemmatize_terms(tokens: list[str]) -> list[str]:
    """
    Input:  list of word tokens
    Output: list of base-form words (e.g., "superconductors" -> "superconductor")
    Use WordNetLemmatizer to lemmatize terms.
    """

def remove_common_words(tokens: list[str]) -> list[str]:
    """
    Input:  list of tokens
    Output: list of tokens excluding stop words like "the", "is", etc.
    Use stopwords to remove common words.
    """

def preprocess_text(text: str) -> list[str]:
    """
    Input:  raw document text
    Output: fully cleaned list of meaningful terms
    Combines the above three steps in order.
    """
