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

def get_collection_main():
    return mongo_database["technical_order_main_class"]
# def get_collection_option():
#     return mongo_database["technical_order_option_class"]
def db_for_subclass():
    return mongo_database["db_for_subclass"]



cursor = db_for_subclass().find({})
main_class_list = []

for document in cursor:
    main_class_list.append(document)

print(main_class_list)


known_sub_classes = [
    "兵科專業專長-兵器課程",
    "兵科專業專長-體能戰技",
    "兵科專業專長 - 體能戰技",
    "兵科專業專長 - 兵器課程",
    "飛行技術-基礎飛行",
    "飛行技術-高級飛行",
    "機型與機身介紹",
    "業專-課器",
    "保養士兵班",
    "測驗與指導",
    "士官分科班",
]


def normalize_class_name(name):
    """去除空白、特殊破折號等符號，使比對更準確"""
    return re.sub(r'[\s－–—﹣]', '', name)


def parse_sub_class(item):
    """解析 sub_class 項目"""
    item = item.strip()
    item = re.sub(r'[－–—﹣]', '-', item)
    item = re.sub(r'\s+', ' ', item)
    normalized_item = normalize_class_name(item)

    for sub_class_prefix in known_sub_classes:
        normalized_prefix = normalize_class_name(sub_class_prefix)

        if normalized_item == normalized_prefix:
            return sub_class_prefix, ""

        if normalized_item.startswith(normalized_prefix):
            match = re.match(rf"^{re.escape(sub_class_prefix)}\s*[-－–—﹣]?\s*(.*)$", item)
            if match:
                option_class = match.group(1).strip()
                return sub_class_prefix, option_class

    return "未分類", item


def extract_sub_class_from_name(name):
    """從 name 拆解出 sub_class"""
    for sub_class in known_sub_classes:
        if sub_class in name:
            return sub_class, name.replace(sub_class, "").replace(" - ", "").strip()
    return "", name


# 處理 main_class_list 資料
# for entry in main_class_list:
#     # 從 name 處理出可能的 sub_class
#     name_sub_class, clean_name = extract_sub_class_from_name(entry["name"])

#     # 如果 sub_class 為空陣列的情況，仍需存資料（沒有 option_class）
#     if not entry["sub_class"]:
#         final_sub_class = name_sub_class if name_sub_class else "未分類"
#         db_for_subclass().update_one(
#             {
#                 "original_id": entry["_id"],
#                 "name": clean_name,
#                 "sub_class": final_sub_class,
#             },
#             {
#                 "$setOnInsert": {
#                     "_id": ObjectId(),
#                     "original_id": entry["_id"],
#                     "name": clean_name,
#                     "sub_class": final_sub_class,
#                     "created_at": datetime.datetime.strptime(entry["created_at"], "%Y-%m-%d %H:%M:%S.%f"),
#                 },
#                 "$set": {
#                     "option_class": []
#                 }
#             },
#             upsert=True,
#         )

#     # 如果 sub_class 有內容，逐項處理
#     for item in entry["sub_class"]:
#         sub_class, option_class = parse_sub_class(item)

#         final_sub_class = sub_class if sub_class != "未分類" else name_sub_class
#         final_option_class = option_class if sub_class != "未分類" else item

#         # 若 name 和 sub_class 仍無法解析，則當成未分類
#         final_sub_class = final_sub_class if final_sub_class else "未分類"

#         # 查找條件
#         query = {
#             "original_id": entry["_id"],
#             "name": clean_name,
#             "sub_class": final_sub_class,
#         }

#         # 更新或插入
#         db_for_subclass().update_one(
#             query,
#             {
#                 "$setOnInsert": {
#                     "_id": ObjectId(),
#                     "original_id": entry["_id"],
#                     "name": clean_name,
#                     "sub_class": final_sub_class,
#                     "created_at": datetime.datetime.strptime(entry["created_at"], "%Y-%m-%d %H:%M:%S.%f"),
#                 },
#                 "$addToSet": {"option_class": final_option_class},  # 避免重複
#             },
#             upsert=True,
#         )

# print("✅ 每個 sub_class 的 option_class 已彙整進陣列，插入 MongoDB！")




