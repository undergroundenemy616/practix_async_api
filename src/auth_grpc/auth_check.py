from functools import wraps
from http import HTTPStatus

import grpc

from core import config

from fastapi import Request, HTTPException

from auth_grpc.auth_pb2 import CheckRoleRequest
from auth_grpc.auth_pb2_grpc import AuthStub


auth_channel = grpc.insecure_channel(
    f"{config.AUTH_GRPC_HOST}:50051"
)
auth_client = AuthStub(auth_channel)


def check_permission(roles: list):
    def check_user_role(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            token = request.headers.get('Authorization', None)
            if not token:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Authorization token needed')
            token = token.replace('Bearer ', '')
            auth_request = CheckRoleRequest(
                access_token=token, roles=' '.join(roles)
            )
            auth_response = auth_client.CheckRole(
                auth_request
            )
            if auth_response.result:
                return await func(*args, request, **kwargs)

            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Dont have an access')
        return wrapper

    return check_user_role
