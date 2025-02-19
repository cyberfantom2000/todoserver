import uuid
from dataclasses import dataclass
from sqlmodel import SQLModel


@dataclass
class ModelCollection:
    public: object
    update: object
    create: object
    id_type: uuid.UUID = uuid.UUID
