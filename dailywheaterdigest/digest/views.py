import logging
import httpx

from django.http import JsonResponse, HttpRequest
from django.conf import settings


logger = logging.getLogger(__name__)


async def index(request: HttpRequest, city:str) -> JsonResponse:
    if not city:
        city = "San Francisco"
    async with httpx.AsyncClient() as client:
        params : dict = {'q': city, 'appid': settings.WEATHER_API_KEY}
        # httpx.ConnectTimeout
        logger.info(params)
        data = await client.get(settings.WEATHER_API_URL, params=params)
    return JsonResponse(data.json())