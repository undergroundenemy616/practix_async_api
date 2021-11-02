INDEX_PERSON_NAME = "person"

INDEX_PERSON_BODY = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
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
            "full_name": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {
                    "raw": {
                        "type": "keyword"
                    }
                }
            },
            "roles": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "birth_date": {
                "type": "date"
            },
            "film_ids": {
                "type": "keyword",
            },
        }
    }
}

TEST_DATA = [
    {"index": {"_index": "person", "_id": "7dcf9ce4-f964-475c-9b38-a69ac8e85b37"}},
    {
        "id": "7dcf9ce4-f964-475c-9b38-a69ac8e85b37",
        "full_name": "Hall Hood",
        "roles": [
            "writer"
        ],
        "film_ids": [
            "3aba7aa0-8930-417c-bf78-3df596c3f062",
            "96198bec-04bf-4ac7-9538-cbf40d1e25db",
            "e44b50ef-485f-46ca-973c-4c78c94b6f73"
        ]
    },
    {"index": {"_index": "person", "_id": "94ccdf0f-a205-409b-8ace-517c91348005"}},
    {
        "id": "94ccdf0f-a205-409b-8ace-517c91348005",
        "full_name": "Arsenio Hall",
        "roles": [
            "actor"
        ],
        "film_ids": [
            "319df05f-c5d9-4389-a84a-a43e695bf000"
        ]
    },
    {"index": {"_index": "person", "_id": "900a4e34-0e3a-47c5-9c9a-06f73d11f395"}},
    {
        "id": "900a4e34-0e3a-47c5-9c9a-06f73d11f395",
        "full_name": "Connie Hall",
        "roles": [
            "actor"
        ],
        "film_ids": [
            "e996369b-d49e-4fbb-8563-c17561dca515"
        ]
    },
    {"index": {"_index": "person", "_id": "c8f4604d-b730-4b13-8588-92356bc22600"}},
    {
        "id": "c8f4604d-b730-4b13-8588-92356bc22600",
        "full_name": "H. Quinn",
        "roles": [
            "director",
            "writer"
        ],
        "film_ids": [
            "3e21bf14-ae47-40f0-b71d-459ec61eb4f8"
        ]
    },
    {"index": {"_index": "person", "_id": "222c4b92-1895-40c7-8b61-98d31b660668"}},
    {
        "id": "222c4b92-1895-40c7-8b61-98d31b660668",
        "full_name": "Samuel L. Jackson",
        "roles": [],
        "film_ids": []
    },
]
