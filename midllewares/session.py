from starlette.middleware.base import BaseHTTPMiddleware


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, repository, engine, allowed_routes: list[str] = None):
        BaseHTTPMiddleware.__init__(self, app)
        self.repo = repository
        self.engine = engine
        self.routes = allowed_routes if allowed_routes is not None else []

    async def dispatch(self, request, call_next):
        fonded = list(filter(lambda el: request.url.path.startswith(el), self.routes))
        if not fonded:
            return await call_next(request)

        try:
            self.repo.open_session(self.engine)
            return await call_next(request)
        finally:
            self.repo.close_session()