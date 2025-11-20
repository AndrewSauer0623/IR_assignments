from typing import List, Dict, Optional
import numpy as np

class Doc:
    def __init__(self,
                 id: str,
                 title: str,
                 text: str,
                 authors: Optional[List[str]] = None,
                 journal: Optional[Dict[str, str]] = None,
                 pub_date: Optional[Dict[str, str]] = None,
                 date_completed: Optional[Dict[str, str]] = None,
                 date_revised: Optional[Dict[str, str]] = None,
                 score: Optional[float] = None,
                 embedding: Optional[np.ndarray] = None):
        self.id = id
        self.title = title
        self.text = text
        self.authors = authors
        self.journal = journal
        self.pub_date = pub_date
        self.date_completed = date_completed
        self.date_revised = date_revised
        self.score = score
        self.embedding = embedding


class Response:
    def __init__(self, 
                 docid: str,
                 answer: str,
                 score: Optional[float] = None):
        self.docid = docid
        self.answer = answer
        self.score = score