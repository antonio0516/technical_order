import re
import traceback
from typing import Union

from fastapi import (APIRouter, File, Form, Header, HTTPException, Request,
                     UploadFile)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.technical_order.Version import Version
from domain.validation.InputValidator import InputValidator

router = APIRouter()


class SaveVersionRequest(BaseModel):
    version_name: str


@router.get("/", status_code=200)
def get_version(
    main_class: Union[str, None] = None,
    sub_class: Union[str, None] = None,
    authorization: str = Header(None),
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    version = Version()
    data = version.get_all_version()

    data = list(data)

    for order in data:
        order["_id"] = str(order["_id"])

    return data


@router.post("/", status_code=201)
async def add_version(request: SaveVersionRequest, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    version = Version()

    version.save_current_version(request.version_name)

    admin_log = AdminLog()
    admin_log.add_log(
        f"新增版本: {request.version_name}",
        jwt_info,
        "新增",
        LogType.INFO,
    )

    return {}


@router.delete("/{version_id}", status_code=200)
def delete_version(
    version_id: str,
    authorization: str = Header(None),
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    version = Version()
    old_version = version.get_version_by_id(version_id)
    version.delete_version_by_id(version_id)

    admin_log = AdminLog()
    admin_log.add_log(
        f"刪除版本: {old_version['version_name']}",
        jwt_info,
        "刪除",
        LogType.CRITICAL,
    )

    return {}


@router.post("/restore/{version_id}", status_code=201)
def restore_version(
    version_id: str,
    authorization: str = Header(None),
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    version = Version()
    version.restore_version_by_id(version_id)

    admin_log = AdminLog()
    admin_log.add_log(
        f"回復版本: {version.get_version_by_id(version_id)['version_name']}",
        jwt_info,
        "回復",
        LogType.CRITICAL,
    )

    return {}
