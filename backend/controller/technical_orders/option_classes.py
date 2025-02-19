from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.technical_order.OptionClass import OptionClass
from domain.validation.InputValidator import InputValidator

router = APIRouter()


@router.get("/", status_code=200)
def get_all_main_classes(authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    option_class = OptionClass()
    data = option_class.get_all()

    return data

@router.get("/{original_id}", status_code=200)
def get_main_classes(original_id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    option_class = OptionClass()
    data = option_class.get_original_main_class(original_id)

    return data

@router.get("/{original_id}/sub_classes", status_code=200)
def get_sub_classes(original_id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = OptionClass()
    data = main_class.get_original_sub_class(original_id)

    return data

@router.get("/{original_id}/{sub_class}/option_class", status_code=200)
def get_option_classes(original_id: str, sub_class: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    main_class = OptionClass()
    data = main_class.get_original_option_class(original_id,sub_class)

    return data