from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.technical_order.MainClass import MainClass
from domain.validation.InputValidator import InputValidator

router = APIRouter()


@router.get("/", status_code=200)
def get_all_main_classes(authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = MainClass()
    data = main_class.get_all()

    return data


@router.post("/", status_code=201)
def add_main_class(request: dict, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = MainClass()

    main_class.add(request["main_class"])

    admin_log = AdminLog()
    admin_log.add_log(
        f"新增主目錄: {request['main_class']}",
        jwt_info,
        "新增",
        LogType.INFO,
    )

    return {}


@router.patch("/{main_class_id}", status_code=200)
def update_main_class(
    main_class_id: str, request: dict, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = MainClass()

    old_name = main_class.get(main_class_id)["name"]

    main_class.update_name(main_class_id, request["main_class"])

    admin_log = AdminLog()
    admin_log.add_log(
        f"將主目錄 {old_name} 重命名為 {request['main_class']}",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.delete("/{main_class_id}", status_code=200)
def deleter_main_class(main_class_id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = MainClass()

    old_name = main_class.get(main_class_id)["name"]

    main_class.delete(main_class_id)

    admin_log = AdminLog()
    admin_log.add_log(
        f"刪除主目錄: {old_name}",
        jwt_info,
        "刪除",
        LogType.CRITICAL,
    )

    return {}


@router.get("/{main_class_id}/sub_classes", status_code=200)
def get_sub_classes(main_class_id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = MainClass()
    data = main_class.get_sub_classes(main_class_id)

    return data


@router.post("/{main_class_id}/sub_classes", status_code=201)
def add_sub_class(main_class_id: str, request: dict, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = MainClass()

    main_class.add_sub_class(main_class_id, request["sub_class"])

    admin_log = AdminLog()
    admin_log.add_log(
        f"新增次目錄: {request['sub_class']}",
        jwt_info,
        "新增",
        LogType.INFO,
    )

    return {}


@router.patch("/{main_class_id}/sub_classes", status_code=200)
def update_sub_class(
    main_class_id: str, request: dict, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    old_sub_class = request["old_sub_class"]
    new_sub_class = request["new_sub_class"]

    main_class = MainClass()

    main_class.update_sub_class(main_class_id, old_sub_class, new_sub_class)

    admin_log = AdminLog()
    admin_log.add_log(
        f"將次目錄 {old_sub_class} 重命名為 {new_sub_class}",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.delete("/{main_class_id}/sub_classes/{sub_class_name}", status_code=200)
def delete_sub_class(
    main_class_id: str, sub_class_name: str, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = MainClass()

    main_class.delete_sub_class(main_class_id, sub_class_name)

    admin_log = AdminLog()
    admin_log.add_log(
        f"刪除次目錄: {sub_class_name}",
        jwt_info,
        "刪除",
        LogType.CRITICAL,
    )

    return {}
