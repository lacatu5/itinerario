from fireo.models import Model
from pydantic import BaseModel


class BaseFirestoreService:
    def __init__(self, model_class: type[Model], schema_class: type[BaseModel]):
        self.model_class = model_class
        self.schema_class = schema_class

    def get(self, id: str) -> BaseModel | None:
        instance = self.model_class.collection.get(id)
        if not instance:
            return None
        return self.schema_class.model_validate(instance)

    def list(
        self,
        filters: dict[str, object] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        skip: int = 0,
    ) -> list[BaseModel]:
        query = self.model_class.collection

        if filters:
            for field, value in filters.items():
                if isinstance(value, dict):
                    operator = value.get("op", "==")
                    filter_value = value.get("value")
                    query = query.filter(field, operator, filter_value)
                else:
                    query = query.filter(field, "==", value)

        if order_by:
            query = query.order(order_by)

        if limit:
            results = query.fetch(limit=limit)
        else:
            results = query.fetch()

        items: list[BaseModel] = [self.schema_class.model_validate(r) for r in results]
        if skip > 0:
            items = items[skip:]
        return items

    def paginate(
        self,
        filters: dict[str, object] | None = None,
        order_by: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, object]:
        query = self.model_class.collection

        if filters:
            for field, value in filters.items():
                if isinstance(value, dict):
                    operator = value.get("op", "==")
                    filter_value = value.get("value")
                    query = query.filter(field, operator, filter_value)
                else:
                    query = query.filter(field, "==", value)

        if order_by:
            query = query.order(order_by)

        results = query.fetch(limit=limit + 1)

        items: list[BaseModel] = [self.schema_class.model_validate(r) for r in results]

        has_more = len(items) > limit
        if has_more:
            items.pop()

        next_cursor = items[-1].id if items else None

        return {
            "items": items,
            "next_cursor": next_cursor,
            "has_more": has_more,
        }

    def create(self, data: BaseModel, user_id: str | None = None) -> BaseModel:
        instance = self.model_class()
        for field, value in data.model_dump().items():
            setattr(instance, field, value)
        if user_id and hasattr(instance, "user_id"):
            instance.user_id = user_id
        instance.save()
        return self.schema_class.model_validate(instance)

    def update(self, id: str, data: BaseModel) -> BaseModel | None:
        instance = self.model_class.collection.get(id)
        if not instance:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        instance.save()
        return self.schema_class.model_validate(instance)

    def delete(self, id: str) -> bool:
        instance = self.model_class.collection.get(id)
        if not instance:
            return False
        instance.delete()
        return True
