import asyncio
import logging
from typing import Callable, Awaitable, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


async def retry(
    action: Callable[[], Awaitable[T]],
    retries: int = 10,
    delay: int = 2,
    name: str = "operation",
) -> T:
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            result = await action()
            logger.info("%s succeeded on attempt %s", name, attempt)
            return result

        except Exception as e:
            last_error = e
            logger.warning(
                "%s failed (%s/%s): %s",
                name,
                attempt,
                retries,
                e,
            )

            await asyncio.sleep(min(delay * attempt, 30))

    raise RuntimeError(f"{name} failed after {retries} attempts") from last_error
