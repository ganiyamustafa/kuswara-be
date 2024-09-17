from pydantic import BaseModel as PydanticBaseModel
from uuid import UUID

class OrmBaseSerializerModel(PydanticBaseModel):
    class Config:
        from_attributes = True

    def dict(self, **kwargs):
        # Customize the dictionary representation here
        original_dict = super().dict(**kwargs)
        for key, val in original_dict.items():
            if isinstance(val, UUID):
                original_dict[key] = str(original_dict[key])

        return original_dict

class MetaResponse(OrmBaseSerializerModel):
    page: int
    limit: int
    total: int
    last_page: int