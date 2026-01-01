from __future__ import annotations

from fireo.fields import DateTime, IDField, TextField
from fireo.models import Model


class Like(Model):
    class Meta:
        collection_name = "likes"

    id = IDField()
    itinerary_id = TextField()
    user_id = TextField()
    comment = TextField(default=None)
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"{self.itinerary_id}_{self.user_id}"
        return super().save(*args, **kwargs)


class Follow(Model):
    class Meta:
        collection_name = "follows"

    id = IDField()
    follower_id = TextField()
    following_id = TextField()
    created_at = DateTime(auto=True)
    updated_at = DateTime(auto=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"{self.follower_id}_{self.following_id}"
        return super().save(*args, **kwargs)
