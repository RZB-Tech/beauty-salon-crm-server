from pydantic import BaseModel, ConfigDict, Field

class SpecializationCreateSchema(BaseModel):
    name: str = Field(..., max_length = 255)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "name": "Парикмахер-стилист"
        }
    })