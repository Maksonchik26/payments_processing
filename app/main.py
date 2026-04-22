import logging
import traceback

import uvicorn
from fastapi import FastAPI, Request, Security, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from app.common.exceptions import InvalidAuthData
from app.config import settings
from app.routers.payments import router as payments_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("uvicorn.error")

API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.STATIC_API_KEY:
        return api_key_header
    else:
        raise InvalidAuthData()

app = FastAPI(dependencies=[Depends(get_api_key)])

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
