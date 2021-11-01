import hashlib


def get_redis_key_hash(index, query, page_size, page_number):
    params = f'{index}::{query}::{page_size}::{page_number}'
    hash_object = hashlib.md5(params.encode())
    return hash_object.hexdigest()
