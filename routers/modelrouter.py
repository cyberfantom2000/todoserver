from typing import Union, Any, List
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .modelcollection import ModelCollection


class QueryModel(BaseModel):
    filters: dict = {}
    fields: list[str] = []


def create_router(manager, model_collections: ModelCollection, *args, **kwargs):
    class ModelRouter:
        def __init__(self, manager, *args, **kwargs):
            self.router = APIRouter(*args, **kwargs)
            self.manager = manager

            self.router.add_api_route('', self.list, methods=['GET'],
                                      response_model=Union[list[model_collections.public], list[dict[str, Any]]])
            self.router.add_api_route('/query', self.query, methods=['POST'],
                                      response_model=Union[list[model_collections.public], list[dict[str, Any]]])
            self.router.add_api_route('', self.create, methods=['POST'],
                                      response_model=Union[model_collections.public, list[model_collections.public]])
            self.router.add_api_route('', self.update, methods=['PATCH'],
                                      response_model=Union[model_collections.public, list[model_collections.public]])
            self.router.add_api_route('', self.delete, methods=['DELETE'], response_class=JSONResponse)

        async def list(self, limit: int = 100, offset: int = 0,
                       fields: str = Query(default=None, description='Comma separated fields')):
            req_fields = fields.split(',') if fields else None
            model_fields = model_collections.public.model_fields
            fields = list(filter(lambda el: el in model_fields, req_fields)) if req_fields else None
            return self.manager.get(limit=limit, offset=offset, fields=fields)

        async def query(self, q: QueryModel):
            model_fields = model_collections.public.model_fields
            fields = list(filter(lambda el: el in model_fields, q.fields)) if q.fields else None
            filters = dict(filter(lambda i: i[0] in model_fields, q.filters.items()))
            return self.manager.get(fields=fields, filters=filters)

        async def create(self, new_el: Union[model_collections.create, List[model_collections.create]]):
            return self.manager.create(new_el)

        async def update(self, update: Union[model_collections.update, List[model_collections.update]]):
            return self.manager.update(update)

        async def delete(self, ids: str = Query(default=None, description='Comma separated ids')):
            remove_ids = ids.split(',') if ids else None
            self.manager.delete(remove_ids)
            return JSONResponse(status_code=200, content=remove_ids)

    return ModelRouter(manager, *args, **kwargs)
