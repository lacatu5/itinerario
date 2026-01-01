from pydantic import BaseModel


def serialize_fireo(fireo_models: list, schema_class: type[BaseModel]) -> list[dict]:
    return [schema_class.model_validate(model).model_dump() for model in fireo_models]


def serialize_fireo_one(
    fireo_model: BaseModel | None, schema_class: type[BaseModel]
) -> dict | None:
    if not fireo_model:
        return None
    return schema_class.model_validate(fireo_model).model_dump()
