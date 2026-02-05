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
    option_class: Union[str, None] = None,
    last_id: Union[str, None] = None,
    original_id: Union[str, None] = None,
    authorization: str = Header(None),
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=False)

    # sub_class = option_class + sub_class
    print("original_id received in API:", original_id)
    order = Order()
    data = order.get_technical_order(
        main_class=main_class, sub_class=sub_class, page_mode=True, last_id=last_id
    )

    data = list(data)
    # print("確保有接到技令資料 : ",data)
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

    image_list = []
    video_list = []
    pdf_list = []
    tag_list = []
    request_data = {}

    option_class = None
    sub_class = None

    for key in form_data.keys():
        if re.match(r"image\[\d+\]", key):
            image_list.append(form_data[key])
        elif re.match(r"video\[\d+\]", key):
            video_list.append(form_data[key])
        elif re.match(r"pdf\[\d+\]", key):
            pdf_list.append(form_data[key])
        elif re.match(r"tag\[\d+\]", key):
            tag_list.append(form_data[key])
        elif key == "optionClass":
            option_class = form_data[key]
        elif key == "subClass":
            sub_class = form_data[key]
        else:
            request_data[key] = form_data[key]

    request_data["tags"] = tag_list

    # 1. 舊資料庫：合併 subClass 和 optionClass
    old_db_data = request_data.copy()
    if option_class and sub_class:
        old_db_data["subClass"] = f"{sub_class} - {option_class}"
    elif sub_class:
        old_db_data["subClass"] = sub_class

    # 2. 新資料庫：分別保存 subClass 和 optionClass
    new_db_data = request_data.copy()
    new_db_data["subClass"] = sub_class if sub_class else ""
    new_db_data["optionClass"] = option_class if option_class else ""

    order = Order()

    if not order.is_file_size_under_limit([image_list, video_list, pdf_list]):
        raise HTTPException(
            status_code=400,
            detail=f"單個檔案大小超過上限：{Order.FILE_SIZE_LIMIT // 1024 // 1024} MB",
        )

    try:
        # 🔧 同時寫入兩個資料庫
        order.add_technical_order(image_list, video_list, pdf_list, old_db_data, new_db_data)
    except Exception as e:
        print(f"新增技令失敗: {str(e)}")
        traceback.print_exc()
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
        # 先驗證 ID 格式
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="無效的技令ID格式")
        
        # 🔧 檢查兩個資料庫中是否有要刪除的技令
        old_order = order.get_order_collection().find_one({"_id": ObjectId(id)})
        new_order = order.get_new_order_collection().find_one({"_id": ObjectId(id)})
        
        if old_order is None and new_order is None:
            raise HTTPException(status_code=404, detail="技令不存在")
        
        # 🔧 決定使用哪個資料作為日誌記錄的來源
        source_order = old_order if old_order else new_order
        source_db = "舊資料庫" if old_order else "新資料庫"
        both_exists = old_order is not None and new_order is not None
        
        if both_exists:
            source_info = "兩個資料庫"
        else:
            source_info = f"{source_db}（將搜尋對應技令）"
        
        print(f"📋 準備刪除技令: {source_order['stepName']} (存在於: {source_info})")
        
        # 🔧 執行刪除操作（會智能搜尋並刪除對應技令）
        order.delete_technical_order(id)
        
        print(f"✅ 技令刪除成功")

        admin_log = AdminLog()
        admin_log.add_log(
            f"刪除技令: {source_order['stepName']} (來源: {source_info})",
            jwt_info,
            "刪除",
            LogType.CRITICAL,
        )

        return {"message": "刪除成功", "source": source_info}

    except HTTPException:
        # 重新拋出 HTTP 異常
        raise
    except Exception as e:
        print(f"❌ 刪除技令失敗: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="刪除失敗")


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

    order = Order()
    
    try:
        # 🔧 先驗證 ID 格式
        if not ObjectId.is_valid(id):
            print(f"❌ 無效的 ObjectId 格式: {id}")
            raise HTTPException(status_code=400, detail="無效的技令ID格式")
        
        # 🔧 檢查舊資料庫是否有此技令
        old_result = order.get_order_collection().find_one({"_id": ObjectId(id)})
        
        # 🔧 檢查新資料庫是否有此技令  
        new_result = order.get_new_order_collection().find_one({"_id": ObjectId(id)})
        
        if old_result is None and new_result is None:
            print(f"❌ 在兩個資料庫中都找不到 ID: {id}")
            # 除錯：檢查資料庫狀態
            old_count = order.get_order_collection().count_documents({})
            new_count = order.get_new_order_collection().count_documents({})
            print(f"舊資料庫技令數量: {old_count}, 新資料庫技令數量: {new_count}")
            raise HTTPException(status_code=404, detail="技令不存在")
        
        # 🔧 決定使用哪個資料作為來源
        source_data = old_result if old_result else new_result
        source_db = "舊資料庫" if old_result else "新資料庫"
        
        print(f"✅ 在{source_db}找到要複製的技令: {source_data.get('stepName', 'Unknown')}")
        
        # 🔧 執行複製操作
        order.duplicate_technical_order(id)
        print("✅ 技令複製成功")
        
        # 🔧 記錄日誌
        admin_log = AdminLog()
        admin_log.add_log(
            f"複製技令: {source_data['stepName']} (來源: {source_db})",
            jwt_info,
            "複製",
            LogType.INFO,
        )
        
        return {
            "message": "複製成功", 
            "source": source_db,
            "original_name": source_data['stepName']
        }
        
    except HTTPException:
        # 重新拋出 HTTP 異常
        raise
    except Exception as e:
        print(f"❌ 複製技令時發生未預期錯誤: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="複製失敗")

@router.get("/{id}", status_code=200)
def get_technical_order_by_id(id: str, authorization: str = Header(None)):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=False)

    order = Order()
    data = order.get_technical_order(technical_order_id=id)

    return data


##########################  嘗試撰寫新的技令後端API 2025/02/26  ########################## 

@router.get("/new/order", status_code=200)
def get_new_technical_order(
    main_class: Union[str, None] = None,
    sub_class: Union[str, None] = None,
    option_class: Union[str, None] = None,
    last_id: Union[str, None] = None,
    original_id: Union[str, None] = None,
    authorization: str = Header(None),
):
    token = None
    if authorization is not None:
        token = authorization.split(" ")[1]

    jwt_info = JWT.jwt_required(token, need_admin=False)

    # sub_class = option_class + sub_class

    order = Order()
    data = order.get_new_technical_order(
        main_class=main_class, sub_class=sub_class, option_class=option_class, page_mode=True, last_id=last_id, original_id=original_id
    )

    data = list(data)
    data = convert_objectid(data)

    for order in data:
        order["_id"] = str(order["_id"])
    # print("comes here means success get data !")
    return data

def convert_objectid(obj):
    if isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj
