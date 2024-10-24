from datetime import datetime

def mongo_to_dict(document):
    doc_dict = document.to_mongo().to_dict()
    for key, value in doc_dict.items():
        if isinstance(value, datetime):
            doc_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    return doc_dict
