from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import OperationalError
from exceptions import *


class ErrorMiddleware(BaseHTTPMiddleware):
    def __int__(self, app):
        BaseHTTPMiddleware.__init__(self, app)

    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except AccessDenied as exc:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={'detail': str(exc)})
        except InvalidCredentials as exc:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'detail': str(exc)})
        except CouldNotValidateCredentials as exc:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'detail': str(exc)})
        except OperationalError as exc:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={'detail': str(exc)})
        except EntityNotFound as exc:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': str(exc)})
        except InvalidArguments as exc:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})
        except InvalidCall as exc:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})
        except UnknownError as exc:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'detail': str(exc)})
