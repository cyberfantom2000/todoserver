import uvicorn
from fastapi import FastAPI

from managers.modelmanager import ModelManager
from routers.modelcollection import ModelCollection
from models.task import TaskPublic, TaskCreate, TaskUpdate
from routers.modelrouter import create_router


app = FastAPI()

router = create_router(object(), ModelCollection(TaskPublic, TaskCreate, TaskUpdate), prefix='/api/task')

app.include_router(router.router)

uvicorn.run(app, host='0.0.0.0', port=8000)
