import os
import re
import traceback
from typing import Union

from bson import ObjectId
from fastapi import (APIRouter, File, Form, Header, HTTPException, Request,
                     UploadFile)
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel

from domain.admin_log import AdminLog, LogType
from domain.auth.Hash import Hash
from domain.auth.JWT import JWT, JWTDecodeError
from domain.database.data_model.User import User
from domain.technical_order.Order import Order
from domain.validation.InputValidator import InputValidator

router = APIRouter()


def file_iterator(file_path: str, buffer_size=1024):
    try:
        # with open(file_path, "rb") as file:
        #     while chunk := file.read(buffer_size):
        #         yield chunk
        with open(file_path, "rb") as file:
            chunk = file.read(buffer_size)
            # 保存當前位置，後面需要從這裡繼續讀取
            position = file.tell()

        # 如果有讀到數據，則進入循環
        while chunk:
            yield chunk  # 返回當前讀取的塊
            with open(file_path, "rb") as file:
                file.seek(position)  # 移動到上次讀取結束的位置
                chunk = file.read(buffer_size)  # 繼續讀取
                position = file.tell()  # 更新位置

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error reading file")


@router.get("/", status_code=200)
def get_technical_order(
    main_class: Union[str, None] = None,
    sub_class: Union[str, None] = None,
    last_id: Union[str, None] = None,
    authorization: str = Header(None),
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=False)

    # sub_class = option_class + sub_class

    order = Order()
    data = order.get_technical_order(
        main_class=main_class, sub_class=sub_class, page_mode=True, last_id=last_id
    )

    data = list(data)

    for order in data:
        order["_id"] = str(order["_id"])

    return data


@router.get("/file/{id}", status_code=200)
def get_technical_order(
    id: str,
):
    order = Order()
    data = order.get_upload_file(id)

    data["_id"] = str(data["_id"])

    return data


@router.get("/image_file/{id}", status_code=200)
def get_technical_order(
    id: str,
):
    order = Order()
    data = order.get_upload_file(id)

    return FileResponse(f"./storage/{id}.{data['extension']}")


@router.get("/pdf_file/{id}", status_code=200)
def get_technical_order(
    id: str,
):
    order = Order()
    data = order.get_upload_file(id)

    # return FileResponse(f"./storage/{id}.{data['extension']}")
    file_path = f"./storage/{id}.{data['extension']}"
    headers = {"Content-Disposition": f"inline; filename={id}.{data['extension']}"}
    return StreamingResponse(
        file_iterator(file_path), headers=headers, media_type="application/pdf"
    )


@router.get("/video_file/{id_might_with_extension}")
async def get_technical_order(request: Request, id_might_with_extension: str):
    if "." in id_might_with_extension:
        id, extension = id_might_with_extension.split(".")
    else:
        id = id_might_with_extension

    order = Order()
    data = order.get_upload_file(id)
    path = f"./storage/{id}.{data['extension']}"

    file_size = os.path.getsize(path)
    range_header = request.headers.get("Range")

    start, end = 0, None
    if range_header:
        start_end = range_header.replace("bytes=", "").split("-")
        start = int(start_end[0])
        end = int(start_end[1]) if start_end[1] else file_size - 1
    else:
        start = 0
        end = min(1024 * 1024, file_size - 1)

    with open(path, mode="rb") as file:
        file.seek(start)
        data = file.read(end - start + 1)
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
        }
        file.close()

    return Response(
        content=data, headers=headers, status_code=206, media_type="video/mp4"
    )


@router.post("/", status_code=201)
async def add_technical_order(request: Request, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    form_data = await request.form()
    print(form_data)

    # iterate form_data
    # save file in form_data
    image_list = []
    video_list = []
    pdf_list = []
    tag_list = []
    request_data = {}

    for key in form_data.keys():
        if re.match(r"image\[\d+\]", key):
            image_list.append(form_data[key])
        elif re.match(r"video\[\d+\]", key):
            video_list.append(form_data[key])
        elif re.match(r"pdf\[\d+\]", key):
            pdf_list.append(form_data[key])
        elif re.match(r"tag\[\d+\]", key):
            tag_list.append(form_data[key])
        else:
            request_data[key] = form_data[key]
    request_data["tags"] = tag_list
    order = Order()

    # check file size
    if order.is_file_size_under_limit([image_list, video_list, pdf_list]) == False:
        raise HTTPException(
            status_code=400,
            detail=f"單個檔案大小超過上限：{Order.FILE_SIZE_LIMIT // 1024 // 1024} MB",
        )

    try:
        order.add_technical_order(image_list, video_list, pdf_list, request_data)
    except:
        raise HTTPException(status_code=500, detail="新增失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"新增技令: {request_data['stepName']}",
        jwt_info,
        "新增",
        LogType.INFO,
    )

    return {}


@router.get("/file_size_limit", status_code=200)
def get_file_size_limit():
    return {"file_size_limit": Order.FILE_SIZE_LIMIT}


@router.delete("/{id}", status_code=200)
async def delete_technical_order(id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    order = Order()
    try:
        old_order = order.get_technical_order(technical_order_id=id)
        order.delete_technical_order(id)

    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="刪除失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"刪除技令: {old_order['stepName']}",
        jwt_info,
        "刪除",
        LogType.CRITICAL,
    )

    return {}


@router.patch("/{id}", status_code=200)
async def update_technical_order(
    id: str, request: Request, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    form_data = await request.form()
    print(form_data)

    # iterate form_data
    # save file in form_data
    image_list = []
    video_list = []
    tag_list = []

    request_data = {}

    for key in form_data.keys():
        if re.match(r"image\[\d+\]", key):
            image_list.append(form_data[key])
        elif re.match(r"video\[\d+\]", key):
            video_list.append(form_data[key])
        elif re.match(r"tag\[\d+\]", key):
            tag_list.append(form_data[key])
        elif (
            "image" not in key
            and "video" not in key
            and "pdf" not in key
            and "tag" not in key
        ):
            request_data[key] = form_data[key]

    request_data["tags"] = tag_list
    print(request_data)

    order = Order()

    # check file size
    if order.is_file_size_under_limit([image_list, video_list]) == False:
        raise HTTPException(
            status_code=400,
            detail=f"單個檔案大小超過上限：{Order.FILE_SIZE_LIMIT // 1024 // 1024} MB",
        )

    print(image_list)
    try:
        old_order = order.get_technical_order(technical_order_id=id)
        order.update_technical_order(id, image_list, video_list, request_data)
    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="更新失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"更新技令: {old_order['stepName']}",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.put("/{id}/images", status_code=200)
async def update_technical_order(
    id: str, request: Request, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    form_data = await request.form()
    print(form_data)

    # iterate form_data
    # save file in form_data
    image_list = []

    request_data = {}

    for key in form_data.keys():
        if re.match(r"image\[\d+\]", key):
            image_list.append(form_data[key])

    print(request_data)

    order = Order()

    # check file size
    if order.is_file_size_under_limit([image_list]) == False:
        raise HTTPException(
            status_code=400,
            detail=f"單個圖片檔案大小超過上限：{Order.FILE_SIZE_LIMIT // 1024 // 1024} MB",
        )

    print(image_list)
    try:
        old_order = order.get_technical_order(technical_order_id=id)
        order.update_technical_order_images(id, image_list)
    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="更新失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"更新技令: {old_order['stepName']} 的圖片",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.put("/{id}/videos", status_code=200)
async def update_technical_order(
    id: str, request: Request, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    form_data = await request.form()
    print(form_data)

    # iterate form_data
    # save file in form_data
    video_list = []

    request_data = {}

    for key in form_data.keys():
        if re.match(r"video\[\d+\]", key):
            video_list.append(form_data[key])

    print(request_data)

    order = Order()

    # check file size
    if order.is_file_size_under_limit([video_list]) == False:
        raise HTTPException(
            status_code=400,
            detail=f"單個影片檔案大小超過上限：{Order.FILE_SIZE_LIMIT // 1024 // 1024} MB",
        )

    print(video_list)
    try:
        old_order = order.get_technical_order(technical_order_id=id)
        order.update_technical_order_videos(id, video_list)
    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="更新失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"更新技令: {old_order['stepName']} 的影片",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.put("/{id}/pdfs", status_code=200)
async def update_technical_order(
    id: str, request: Request, authorization: str = Header(None)
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    form_data = await request.form()
    print(form_data)

    # iterate form_data
    # save file in form_data
    pdf_list = []

    request_data = {}

    for key in form_data.keys():
        if re.match(r"pdf\[\d+\]", key):
            pdf_list.append(form_data[key])

    print(request_data)

    order = Order()

    print(pdf_list)

    # check file size
    if order.is_file_size_under_limit([pdf_list]) == False:
        raise HTTPException(
            status_code=400,
            detail=f"單個 PDF 檔案大小超過上限：{Order.FILE_SIZE_LIMIT // 1024 // 1024} MB",
        )

    try:
        old_order = order.get_technical_order(technical_order_id=id)
        order.update_technical_order_pdfs(id, pdf_list)
    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="更新失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"更新技令: {old_order['stepName']} 的 pdf",
        jwt_info,
        "更新",
        LogType.WARNING,
    )

    return {}


@router.post("/duplicate/{id}", status_code=201)
async def duplicate_technical_order(id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=True)

    # check if the order exists
    result = Order().get_technical_order(technical_order_id=ObjectId(id))
    if result is None:
        raise HTTPException(status_code=404, detail="技令不存在")

    order = Order()
    try:
        old_order = order.get_technical_order(technical_order_id=id)
        order.duplicate_technical_order(id)
    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="複製失敗")

    admin_log = AdminLog()
    admin_log.add_log(
        f"複製技令: {old_order['stepName']}",
        jwt_info,
        "複製",
        LogType.INFO,
    )

    return {}


@router.get("/{id}", status_code=200)
def get_technical_order_by_id(id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=False)

    order = Order()
    data = order.get_technical_order(technical_order_id=id)

    return data
