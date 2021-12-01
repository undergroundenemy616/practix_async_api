import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi import Request, HTTPException

from api.v1 import film, genre, person
from core import config
from db import elastic, redis
from tracer import tracer

app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.middleware("http")
async def add_tracing(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required')
    response = await call_next(request)
    with tracer.start_span(request.url.path) as span:
        request_id = request.headers.get('X-Request-Id')
        span.set_tag('http.request_id', request_id)
        span.set_tag('http.url', request.url)
        span.set_tag('http.method', request.method)
        span.set_tag('http.status_code', response.status_code)
    return response


app.include_router(film.router, prefix='/api/v1/film', tags=['film'])
app.include_router(genre.router, prefix='/api/v1/genre', tags=['genre'])
app.include_router(person.router, prefix='/api/v1/person', tags=['person'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
