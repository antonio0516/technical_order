import pymongo
import datetime
from domain.get_config import Config
from fastapi import HTTPException
import pymongo
import datetime
from bson.objectid import ObjectId
import re
CONFIG = Config.get_config()

mongo_db_url = (
    f"mongodb://{CONFIG.mongo_db['admin']}:{CONFIG.mongo_db['password']}@"
    + f"{CONFIG.mongo_db['host']}:{CONFIG.mongo_db['port']}"
)

mongo_client = pymongo.MongoClient(mongo_db_url)
mongo_database = mongo_client["technical_order_editor_db"]


def db_for_technical_order():
    return mongo_database["technical_order"]

def new_db_technical_order():
    return mongo_database["new_technical_order"]

# cursor = db_for_technical_order().find({})

# for document in cursor:
#     # 確保 `_id` 是 `ObjectId`
#     document["_id"] = ObjectId(document["_id"])
    
#     # 確保 `tags` 是 `ObjectId` 陣列
#     document["tags"] = [ObjectId(tag) for tag in document.get("tags", [])]

#     # 拆分 `subClass`
#     if "subClass" in document and " - " in document["subClass"]:
#         split_values = document["subClass"].split(" - ", 1)
#         sub_class_value = split_values[0]  # 兵科專業專長-兵器課程
#         option_class_value = split_values[1]  # 各型機每日全區檢查及保養實作(模擬機7)28
#     else:
#         sub_class_value = document.get("subClass", "")
#         option_class_value = ""

#     # 重新組裝 document，確保 `optionClass` 在 `subClass` 旁邊
#     new_document = {
#         "_id": document["_id"],
#         "stepName": document.get("stepName", ""),
#         "stepNumber": document.get("stepNumber", ""),
#         "mainClass": document.get("mainClass", ""),
#         "subClass": sub_class_value,
#         "optionClass": option_class_value,  # 🆕 改名並移到 subClass 旁邊
#         "說明描述": document.get("說明描述", ""),
#         "image_id_list": document.get("image_id_list", []),
#         "video_id_list": document.get("video_id_list", []),
#         "pdf_id_list": document.get("pdf_id_list", []),
#         "tags": document.get("tags", []),
#         "sort_tags": document.get("sort_tags", ""),
#         "sort_step_number": document.get("sort_step_number", ""),
#     }

#     # 插入到新資料庫
#     new_db_technical_order().insert_one(new_document)
# print("✅ 資料轉移成功！")


# new_db_technical_order().create_index([("mainClass", 1), ("subClass", 1), ("optionClass", 1), ("sort_tags", 1), ("sort_step_number", 1)])

# print("✅ 已成功新增索引")









