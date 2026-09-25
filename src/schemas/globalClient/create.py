from pydantic import BaseModel, ConfigDict, Field

class GlobalClientContactSchema(BaseModel):
    # Raw `response` string from WebApp.requestContact's callback - signed by Telegram like initData
    response: str = Field(min_length = 1)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "response": "contact=%7B%22user_id%22%3A123456789%2C%22phone_number%22%3A%22998901112233%22%2C%22first_name%22%3A%22Anna%22%7D&auth_date=1758800000&hash=..."
        }
    })
