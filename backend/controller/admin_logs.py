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
from domain.validation.InputValidator import InputValidator

router = APIRouter()


class StudentLoginRequest(BaseModel):
    student_number: str
    password: str


class ResetAllStudentRequest(BaseModel):
    start_number: int
    end_number: int


class PostStudentGradeRequest(BaseModel):
    exam_token: str
    grade: int


@router.get("/", status_code=200)
def get_admin_logs(
    authorization: str = Header(None),
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    admin_log = AdminLog()
    data = admin_log.get_all_log()

    data = list(data)

    for log in data:
        log["_id"] = str(log["_id"])

    return data
