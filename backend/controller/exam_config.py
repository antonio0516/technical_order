import os
import re
import shutil
import time
import traceback
from typing import Union

import aspose.words as aw
import docx
from docxcompose.composer import Composer
from fastapi import (APIRouter, File, Form, Header, HTTPException, Request,
                     UploadFile)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.database.database import mongo_client
from domain.exam.exam_config import ExamConfig, ExamConfigColumn
from domain.exam.student import Student
from domain.validation.InputValidator import InputValidator

router = APIRouter()


class UpdateExamTimeRequest(BaseModel):
    exam_time: int


@router.put("/exam_time", status_code=200)
def update_exam_time(request: UpdateExamTimeRequest, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    if request.exam_time < 0:
        raise HTTPException(status_code=400, detail="考試時間不能小於 0")

    try:
        exam_time = int(request.exam_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail="考試時間格式錯誤")

    try:
        with mongo_client.start_session() as session:
            with session.start_transaction():
                exam_config = ExamConfig()
                exam_config.set_exam_config_column(
                    ExamConfigColumn.EXAM_TIME, exam_time
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail="設置考試時間失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"設置考試時間為{exam_time}秒",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.get("/exam_time", status_code=200)
def get_exam_time():
    try:
        exam_config = ExamConfig()
        exam_time = exam_config.get_exam_config_column(ExamConfigColumn.EXAM_TIME)
        return {"exam_time": exam_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail="獲取考試時間失敗")
