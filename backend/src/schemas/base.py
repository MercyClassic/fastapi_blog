from pydantic import BaseModel, validator


class CreatedAtBaseSchema(BaseModel):
    created_at: str

    @validator('created_at', pre=True)
    def parse_created_at(cls, value):
        return value.strftime('%Y-%m-%d %H:%M:%S')
