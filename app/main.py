import logging
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.error_handlers import api_error_handler, custom_405_handler, custom_422_handler, custom_http_exception_handler
from app.common.exceptions import APIError
from app.infrastructure.messaging.broker.broker import broker
from app.routers.payments import router as payments_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("uvicorn.error")

app = FastAPI()


app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(status.HTTP_405_METHOD_NOT_ALLOWED, custom_405_handler)
app.add_exception_handler(RequestValidationError, custom_422_handler)
app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, custom_http_exception_handler)

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"🚨 Unhandled exception at {request.url}: {exc}")
        logger.error(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )

app.include_router(payments_router, prefix="/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
