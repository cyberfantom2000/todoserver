import uuid
from collections.abc import Iterable

from exceptions import EntityNotFound
from utils import is_models_collection


class ModelManager:
    def __init__(self, repo, model):
        self.repo = repo
        self.model = model

    def create(self, to_create):
        if is_models_collection(to_create):
            return self.repo.create_all(self.model, to_create)
        else:
            return self.repo.create(self.model, model_data=to_create)

    def update(self, to_update):
        is_collection = is_models_collection(to_update)
        if is_collection:
            updatable = self.repo.get_item(self.model, filters={'id': [el.id for el in to_update]})
        else:
            updatable = self.repo.get_item(self.model, filters={'id': to_update.id})

        if updatable is None or not updatable:
            raise EntityNotFound(str(self.model))

        if is_collection:
            return self.repo.update_all(updatable, to_update)
        else:
            return self.repo.update(updatable, obj=to_update)

    def delete(self, model_id):
        item = self.repo.get_item(self.model, filters={'id': model_id})
        if item is None or not item:
            raise EntityNotFound(str(self.model))
        return self.repo.delete(item)

    def get(self, *args, filters: dict | None = None, limit: int = None, offset: int = None, fields: list[str] = None):
        self._handle_filters(filters)

        if fields:
            fields = list(filter(lambda el: el in self.model.model_fields, fields))
            attrs = [getattr(self.model, field) for field in fields]
            result = self.repo.get_fields(self.model, *attrs, filters=filters, offset=offset, limit=limit)
            return self._zip_query_result(fields, result)
        else:
            return self.repo.get_items(self.model, filters=filters, offset=offset, limit=limit)

    @staticmethod
    def _zip_query_result(fields: list[str], query_result: list) -> list:
        if len(fields) == 1:
            return [dict(zip(fields, [value])) for value in query_result]
        else:
            return [dict(zip(fields, values)) for values in query_result]

    @staticmethod
    def _handle_filters(filters: dict | None):
        if not filters:
            return filters

        if 'id' in filters:
            if not filters['id']:
                del filters['id']
            else:
                if not isinstance(filters['id'], str) and isinstance(filters['id'], Iterable):
                    filters['id'] = [uuid.UUID(el) for el in filters['id']]
                else:
                    filters['id'] = uuid.UUID(filters['id'])
