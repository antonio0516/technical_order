from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.technical_order.OrderTemplate import OrderTemplate
from domain.validation.InputValidator import InputValidator

router = APIRouter()


@router.get("/", status_code=200)
def get_all_order_template_columns(authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    order_template = OrderTemplate()
    data = order_template.get_all_order_template_column()

    return data


@router.post("/", status_code=201)
def add_order_template_column(request: dict, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    order_template = OrderTemplate()

    order_template.add_order_template_column(
        {"name": request["name"], "type": request["type"]}
    )

    admin_log = AdminLog()
    admin_log.add_log(
        f"新增技令樣板欄位: {request['name']}",
        jwt_info,
        "新增",
        LogType.INFO,
    )

    return {}


@router.patch("/{order_template_column_id}", status_code=200)
def update_order_template_column(
    order_template_column_id: str, request: dict, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    order_template = OrderTemplate()

    old_column_name = order_template.get_order_template_column(
        order_template_column_id
    )["name"]

    order_template.update_order_template_column_name(
        order_template_column_id, request["new_column_name"]
    )

    admin_log = AdminLog()
    admin_log.add_log(
        f"將技令樣板欄位 {old_column_name} 重命名為 {request['new_column_name']}",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.delete("/{order_template_column_id}", status_code=200)
def delete_order_template_column(
    order_template_column_id: str, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    order_template = OrderTemplate()

    deleted_column = order_template.get_order_template_column(order_template_column_id)

    order_template.delete_order_template_column(order_template_column_id)

    admin_log = AdminLog()
    admin_log.add_log(
        f"刪除技令樣板欄位: {deleted_column['name']}",
        jwt_info,
        "刪除",
        LogType.CRITICAL,
    )

    return {}


@router.get("/types", status_code=200)
def get_all_order_template_column_type(authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    order_template = OrderTemplate()
    data = order_template.get_all_order_template_column_type()

    return data
