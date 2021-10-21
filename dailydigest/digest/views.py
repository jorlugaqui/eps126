import asyncio
import logging

import httpx

from django.http import JsonResponse, HttpRequest
from django.conf import settings


logger = logging.getLogger(__name__)


async def index(request: HttpRequest, city:str="San Francisco") -> JsonResponse:
    response: dict = {}
    error_message: str = ''
    http_status_code: int = 200
    digest_tasks: list = []

    async with httpx.AsyncClient() as client:
        try:
            digest_tasks.append(asyncio.ensure_future(get_weather_digest(client, city)))
            future_results  = await asyncio.gather(*digest_tasks)
            for result in future_results:
               response = __prepare_response_data(result)
        except httpx.ConnectTimeout as e:
            error_message: str = f'Internal API call timed out: {e}'
            http_status_code = 500
            logger.error(error_message, exc_info=True)
        except KeyError as e:
            error_message = f'Malformed response: {e}'
            http_status_code = 500
            logger.error(error_message, exc_info=True)
        except ConnectionError as e:
            error_message = f'Error while performing an internal API call: {e}'
            http_status_code = 500
            logger.error(error_message, exc_info=True)
        except Exception as e:
            error_message = f'Internal server error: {e}'
            http_status_code = 500
            logger.error(error_message, exc_info=True)

    if error_message:
        response['data'] = {}
        response['error'] = error_message
        response['http_status_code'] = http_status_code

    return JsonResponse(response, status=response.get('http_status_code'))


async def get_weather_digest(client: httpx.AsyncClient, city: str) -> dict:
    params : dict = {'q': city, 'appid': settings.WEATHER_API_KEY}
    logger.info(f'Calling openweathermap service for ${city}')
    data = await client.get(settings.WEATHER_API_URL, params=params)
    return {'name': 'weather', 'data': data.json()}


def __prepare_weather_response(data: dict) -> dict:
    if data.get('cod', 200) >= 400:
        logger.error('Weather API call returned with an error')
        raise ConnectionError(f'http_status_code: {data.get("cod")} message: {data.get("message")}')

    return {
        'data': data,
        'error': None,
        'http_status_code': data.get('cod')
    }


def __prepare_response_data(response: dict) -> dict:
    format_response = {
        'weather': __prepare_weather_response
    }

    return format_response.get(response.get('name'))(response.get('data'))