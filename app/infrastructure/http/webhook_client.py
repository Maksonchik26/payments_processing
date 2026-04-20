import httpx

async def send_webhook(url: str, payload: dict):
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
