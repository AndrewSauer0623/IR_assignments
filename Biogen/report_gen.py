from typing import List, Dict
import json
from structures import Response, Doc

def generate_biogen_report(responses: List[Response],
                           question_id: str,
                           doc_lookup: Dict[str, Doc] = None,
                           output_file: str = "biogen_report.json") -> None:
    # prepare the answers array
    answers = []
    for resp in responses:
        entry = {
            "doc_id": resp.docid,
            "text": resp.answer
        }
        # optionally include score if present
        if resp.score is not None:
            entry["score"] = resp.score

        # optionally add metadata from Doc
        if doc_lookup and resp.docid in doc_lookup:
            doc = doc_lookup[resp.docid]
            entry["title"] = doc.title
            entry["authors"] = doc.authors
            entry["journal"] = doc.journal
            entry["pub_date"] = doc.pub_date
        answers.append(entry)
    # assemble final JSON structure
    report = {
        "question_id": question_id,
        "answers": answers
    }
    # write to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
