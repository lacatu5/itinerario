from fireo.fields import DateTime, IDField, ListField, TextField
from fireo.models import Model


class Conversation(Model):
    class Meta:
        collection_name = "conversations"

    id = IDField()
    participants = ListField()
    last_message_at = DateTime(default=None)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)


class Message(Model):
    class Meta:
        collection_name = "messages"

    id = IDField()
    conversation_id = TextField()
    sender_id = TextField()
    content = TextField()
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)
