from datetime import datetime, timezone
from bson import ObjectId


PROVIDERS = ['gemini', 'openai', 'claude']


def create_api_key(db, fernet, provider, key, name=''):
    encrypted = fernet.encrypt(key.encode()).decode()
    doc = {
        'provider': provider,
        'key': encrypted,
        'name': name or f'{provider} key',
        'is_active': True,
        'usage_count': 0,
        'last_used_at': None,
        'error_count': 0,
        'created_at': datetime.now(timezone.utc),
    }
    result = db.api_keys.insert_one(doc)
    return str(result.inserted_id)


def get_all_api_keys(db):
    return list(db.api_keys.find().sort('created_at', -1))


def get_api_key(db, key_id):
    return db.api_keys.find_one({'_id': ObjectId(key_id)})


def decrypt_key(fernet, encrypted_key):
    return fernet.decrypt(encrypted_key.encode()).decode()


def delete_api_key(db, key_id):
    db.api_keys.delete_one({'_id': ObjectId(key_id)})


def toggle_api_key(db, key_id):
    doc = db.api_keys.find_one({'_id': ObjectId(key_id)})
    if doc:
        db.api_keys.update_one(
            {'_id': ObjectId(key_id)},
            {'$set': {'is_active': not doc['is_active']}}
        )


def get_next_key(db, fernet, provider):
    """Round-robin key selection: pick the least-recently-used active key."""
    key_doc = db.api_keys.find_one(
        {'provider': provider, 'is_active': True},
        sort=[('last_used_at', 1)]
    )
    if not key_doc:
        return None, None
    db.api_keys.update_one(
        {'_id': key_doc['_id']},
        {
            '$set': {'last_used_at': datetime.now(timezone.utc)},
            '$inc': {'usage_count': 1}
        }
    )
    return str(key_doc['_id']), decrypt_key(fernet, key_doc['key'])


def record_key_error(db, key_id, max_errors=5):
    """Increment error count; disable key after max_errors consecutive failures."""
    result = db.api_keys.find_one_and_update(
        {'_id': ObjectId(key_id)},
        {'$inc': {'error_count': 1}},
        return_document=True
    )
    if result and result['error_count'] >= max_errors:
        db.api_keys.update_one(
            {'_id': ObjectId(key_id)},
            {'$set': {'is_active': False}}
        )


def reset_key_errors(db, key_id):
    db.api_keys.update_one(
        {'_id': ObjectId(key_id)},
        {'$set': {'error_count': 0}}
    )
