from sqlmodel import Session, select, and_, SQLModel, or_
from collections.abc import Iterable
from utils import is_models_collection


# TODO filter mapper: example gt__id=1,
class Repository:
    def __init__(self):
        self.session = None

    def open_session(self, engine):
        self.session = Session(engine)

    def close_session(self):
        self.session.close()

    def get_item(self, model, *, filters=None):
        res = self.get_items(model, filters=filters)
        return res[0] if len(res) else None

    def get_fields(self, model, *fields, filters=None, limit=None, offset=None) -> list:
        conditions = self._to_conditions(model, filters)
        return self.get(*fields or (model,), conditions=conditions, session=self.session, limit=limit, offset=offset)

    def get_items(self, model, *, filters=None, limit=None, offset=None) -> list[SQLModel]:
        conditions = self._to_conditions(model, filters)
        return self.get(model, conditions=conditions, session=self.session, limit=limit, offset=offset)

    @staticmethod
    def get(*args, conditions, session, limit, offset) -> list[SQLModel] | SQLModel:
        try:
            statement = select(*args)
            if limit:
                statement = statement.limit(limit)
            if offset:
                statement = statement.offset(offset)
            if conditions:
                statement = statement.where(and_(*conditions))

            res = session.exec(statement).all()
            return list(res)
        except Exception as e:
            session.rollback()
            raise e

    def create(self, model_type, model_data=None, **kwargs) -> SQLModel:
        if model_data:
            new = model_type.model_validate(model_data)
        else:
            new = model_type(**kwargs)
        self._add_and_commit(new, self.session)
        self.session.refresh(new)
        return new

    def create_all(self, model_type, models) -> list[SQLModel]:
        elements = []
        for m in models:
            elements.append(model_type.model_validate(m))

        self._add_and_commit(models, self.session)

        for el in elements:
            self.session.refresh(el)

        return elements

    def update(self, model, obj=None, **kwargs) -> SQLModel:
        if obj:
            exclude_fields = set(obj.model_fields.keys()) - set(model.model_fields.keys())
            return self.update(model, **obj.model_dump(exclude_unset=True, exclude_none=True, exclude=exclude_fields))
        if kwargs:
            for key, val in kwargs.items():
                if key != 'id':
                    setattr(model, key, val)

        self._add_and_commit(model, self.session)
        self.session.refresh(model)

        return model

    def update_all(self, updatable, updates) -> list[SQLModel]:
        for model, new_model in zip(updatable, updates):
            exclude_fields = set(new_model.model_fields.keys()) - set(model.model_fields.keys())
            exclude_fields.add('id')
            data = new_model.model_dump(exclude_unset=True, exclude_none=True, exclude=exclude_fields)
            for key, val in data.items():
                setattr(model, key, val)
        self._add_and_commit(updatable, self.session)

        for el in updatable:
            self.session.refresh(el)

        return updatable

    def delete(self, models) -> None:
        self._delete(models if is_models_collection(models) else [models], self.session)

    def commit(self, to_commit) -> SQLModel:
        self._add_and_commit(to_commit, self.session)
        if not is_models_collection(to_commit):
            to_commit = [to_commit]

        for el in to_commit:
            self.session.refresh(el)

        return to_commit if is_models_collection(to_commit) else to_commit[0]

    @staticmethod
    def _delete(models, session) -> None:
        try:
            for model in models:
                session.delete(model)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def _add(data, session) -> None:
        try:
            if is_models_collection(data):
                session.add_all(data)
            else:
                session.add(data)
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def _commit(session):
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def _add_and_commit(data, session) -> None:
        Repository._add(data, session)
        Repository._commit(session)

    @staticmethod
    def _to_conditions(model, filters) -> list:
        if filters:
            result = []
            for key, val in filters.items():
                if not isinstance(val, str) and isinstance(val, Iterable):
                    result.append(or_(*[getattr(model, key) == el for el in val]))
                else:
                    result.append(getattr(model, key) == val)
            return result
        else:
            return []
