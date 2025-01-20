from typing import Iterable
from sqlmodel import SQLModel


def is_models_collection(model):
    return not isinstance(model, SQLModel) and isinstance(model, Iterable)
