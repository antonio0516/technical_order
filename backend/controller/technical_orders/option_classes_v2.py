from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.technical_order.OptionClassV2 import OptionClassV2
from domain.validation.InputValidator import InputValidator

router = APIRouter()


@router.get("/", status_code=200)
def get_all_main_classes(authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    option_class_v2 = OptionClassV2()
    data = option_class_v2.get_all()
    
    return data

@router.get("/{_id}", status_code=200)
def get_main_classes(_id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    option_class_v2 = OptionClassV2()
    data = option_class_v2.get_main_class(_id)

    return data

@router.get("/{_id}/sub_class", status_code=200)
def get_sub_classes(_id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = OptionClassV2()
    data = main_class.get_sub_class(_id)

    return data
@router.get("/{_id}/{sub_class}/option_class", status_code=200)
def get_option_classes(_id: str, sub_class: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class_v2 = OptionClassV2()
    data = main_class_v2.get_option_class(_id,sub_class)

    return data