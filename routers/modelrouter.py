from typing import Union, Any, List
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .modelcollection import ModelCollection


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
            fields = list(filter(lambda el: el in manager.model.model_fields, req_fields)) if req_fields else None
            return self.manager.get(limit=limit, offset=offset, fields=fields)

        async def query(self, filters: dict = Query(default={}), fields: list = Query(default=[])):
            model_fields = manager.model.model_fields
            fields = list(filter(lambda el: el in model_fields, fields)) if fields else None
            filters = dict(filter(lambda i: i[0] in model_fields, filters.items()))
            return self.manager.get(fields=fields, filters=filters)

        async def create(self, new_el: Union[model_collections.create, List[model_collections.create]]):
            a = self.manager.create(new_el)
            return a

        async def update(self, update: Union[model_collections.update, List[model_collections.update]]):
            return self.manager.update(update)

        async def delete(self, uid: str = Query(default=None, description='Comma separated fields')):
            req_fields = uid.split(',') if uid else None
            self.manager.delete(req_fields)
            return JSONResponse(status_code=200, content=req_fields)

    return ModelRouter(manager, *args, **kwargs)
