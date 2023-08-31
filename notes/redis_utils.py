import json

import redis


class RedisCrud:
    client = redis.Redis(host='localhost', port=6379, db=1)

    @classmethod
    def save_note_in_redis(cls, note: dict, user_id: int):
        user_id = f"user_{user_id}"
        note_id = f"note_{note.get('id')}"
        cls.client.hset(user_id, note_id, json.dumps(note))

    @classmethod
    def get_notes_by_user_id(cls, user_id: int):
        user_id = f"user_{user_id}"
        notes_dict = cls.client.hgetall(user_id)
        if notes_dict:
            notes_dict = [json.loads(x) for x in notes_dict.values()]
        return notes_dict

    @classmethod
    def delete_note_in_redis(cls, note_id: int, user_id: int):
        user_id = f"user_{user_id}"
        note_id = f"note_{note_id}"
        cls.client.hdel(user_id, note_id)

