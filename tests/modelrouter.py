import unittest
from unittest.mock import MagicMock
from sqlmodel import SQLModel

from routers.modelrouter import create_router, ModelCollection, QueryModel


class MockModelBase(SQLModel):
    id: int
    name: str


class MockModel(MockModelBase):
    secret: str
    mail: str


class MockModelPublic(MockModelBase):
    pass


class MockModelUpdate(MockModelBase):
    id: int
    name: str | None = None


class MockModelCreate(SQLModel):
    name: str
    mail: str
    secret: str


class ModelRouterTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        collection_mock = ModelCollection(public=MockModelPublic, update=MockModelUpdate, create=MockModelCreate)
        manager_mock = MagicMock()
        manager_mock.get = MagicMock()
        manager_mock.create = MagicMock()
        manager_mock.delete = MagicMock()

        self.router = create_router(manager_mock, collection_mock)

    async def test_list_request(self):
        limit = 10
        offset = 2
        fields = 'id,secret,name,mail'

        await self.router.list(limit, offset, fields)

        self.assertEqual({'limit': limit, 'offset': offset, 'fields': ['id', 'name']},
                         self.router.manager.get.call_args.kwargs)

    async def test_query_request(self):
        model = QueryModel(filters={'id': [1, 2, 3], 'not': 'exists'}, fields=['name', 'secret'])

        await self.router.query(model)

        self.router.manager.get.assert_called_with(fields=['name'], filters={'id': [1, 2, 3]})

    async def test_create_request(self):
        model = MockModelCreate(name='name', secret='123', mail='mail.ru')

        await self.router.create(model)

        self.router.manager.create.assert_called_with(model)

    async def test_update_request(self):
        model = MockModelUpdate(id=2, name='test')

        await self.router.update(model)

        self.router.manager.update.assert_called_with(model)
