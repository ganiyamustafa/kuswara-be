import math
from fastapi.encoders import jsonable_encoder
from fastapi import Request, HTTPException
from fastapi_async_sqlalchemy import db
from sqlalchemy import select, func, Select, text
from typing import Union, Callable, Any
from http import HTTPStatus
from middleware.log import logging

class SuccessResponse:
    def __init__(self, data: dict, meta: Union[dict, None], message: str):
        self.data = data
        self.meta = meta
        self.message = message

    def to_json(self):
        if self.meta != None:
            return {
                'message': self.message,
                'data': self.data,
                'meta': self.meta
            }
        else:
            return {
                'message': self.message,
                'data': self.data
            }

async def safe_function(f: Callable[..., Any], *args: Any, **kwargs: Any):
    try:
        return await f(*args, **kwargs)
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f'==== internal server error occured ======: {e}')
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='something went wrong')

def exclude_password(obj):
    data = jsonable_encoder(obj)
    data.pop("password", None)
    return data

async def paginate_api(request: Request, base_query: Select):
    query = request.query_params
    page, limit = query.get('page') or 1, query.get('limit') or 20
    page, limit = int(page), int(limit)
    offset = ((page - 1) * limit)

    count_q = select(func.count().label('id')).select_from(base_query.alias())
    count = (await db.session.execute(count_q)).scalar()

    order_by, sort = request.get("order_by"), request.get('sort')
    if order_by and sort:
        base_query = base_query.order_by(text(f'{order_by} {sort}'))

    if limit > 0:
        base_query = base_query.limit(limit).offset(offset)
    else:
        limit = count
        
    last_page = math.ceil(count/limit) if count > 0 else 1

    return base_query, page, limit, count, last_page
