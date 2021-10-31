INDEX_GENRE_NAME = "genre"

INDEX_GENRE_BODY = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "name": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            }
        }
    }
}

TEST_DATA = [
    {"index": {"_index": "genre", "_id": "f994fbe7-88f0-4d93-a060-55c15e553dff"}},
    {"id": "f994fbe7-88f0-4d93-a060-55c15e553dff", "name": "\u0444\u043e\u043d\u043aeqwddsa",
     "description": "description14"},
    {"index": {"_index": "genre", "_id": "f83d58c3-a2d6-454c-a39d-e37d06173fd3"}},
    {"id": "f83d58c3-a2d6-454c-a39d-e37d06173fd3", "name": "phonkdas", "description": "description5"},
    {"index": {"_index": "genre", "_id": "ea736384-c5bf-40c6-a7eb-2407e9e9b16c"}},
    {"id": "ea736384-c5bf-40c6-a7eb-2407e9e9b16c", "name": "sexdsa", "description": "description12"},
    {"index": {"_index": "genre", "_id": "e1002d12-d323-4519-9410-7b06be7e4174"}},
    {"id": "e1002d12-d323-4519-9410-7b06be7e4174", "name": "\u0441\u0435\u043a\u0441das",
     "description": "description9dsadsa"},
    {"index": {"_index": "genre", "_id": "add65955-dea6-4187-b7bc-5c5110727571"}},
    {"id": "add65955-dea6-4187-b7bc-5c5110727571", "name": "genre7dasdsadsadsadas", "description": "description7"},
    {"index": {"_index": "genre", "_id": "63a67ed1-d5ee-4912-86b0-a6744a8bbf55"}},
    {"id": "63a67ed1-d5ee-4912-86b0-a6744a8bbf55", "name": "genre13dsadsadsadsada", "description": "description13"},
    {"index": {"_index": "genre", "_id": "3c269046-ab33-490c-9f42-937f24dc25a5"}},
    {"id": "3c269046-ab33-490c-9f42-937f24dc25a5", "name": "genre8dsadsadsadsa", "description": "description8"}
]
