from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.technical_order.Tag import Tag
from domain.validation.InputValidator import InputValidator

router = APIRouter()


@router.get("/", status_code=200)
def get_all_tags(authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    tag = Tag()
    data = tag.get_all()

    return data


@router.post("/", status_code=201)
def add_tag(request: dict, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    tag = Tag()

    tag.add(request["name"])

    admin_log = AdminLog()
    admin_log.add_log(
        f"新增標籤: {request['name']}",
        jwt_info,
        "新增",
        LogType.INFO,
    )

    return {}


@router.patch("/{tag_id}", status_code=200)
def update_tag(tag_id: str, request: dict, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    tag = Tag()

    old_name = tag.get(tag_id)["name"]

    tag.update_name(tag_id, request["name"])

    admin_log = AdminLog()
    admin_log.add_log(
        f"將標籤 {old_name} 重命名為 {request['name']}",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.delete("/{tag_id}", status_code=200)
def deleter_tag(tag_id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    tag = Tag()

    old_name = tag.get(tag_id)["name"]

    tag.delete(tag_id)

    admin_log = AdminLog()
    admin_log.add_log(
        f"刪除標籤: {old_name}",
        jwt_info,
        "刪除",
        LogType.CRITICAL,
    )

    return {}
