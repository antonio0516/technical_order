import datetime
import traceback

from bson.objectid import ObjectId
from fastapi import HTTPException

from domain.database.database import mongo_client, mongo_database
from domain.technical_order.Order import Order

class OptionClassV2:
    def __init__(self):
        pass
    def get_collection(self):
        return mongo_database["db_for_subclass_v3"]
    def get_all(self):
        
        result = self.get_collection().find({})
        result_list = []
        for inside in result:
            inside["original_id"] = str(inside["original_id"])
            inside["_id"] = str(inside["_id"])
            result_list.append(inside)
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return result_list


    def get_main_class(self, _id: str):
        """
        根據 original_id 查詢所有符合的資料
        """
        print("here")
        _id = _id.strip() 
        if _id == "all":
            cursor = self.get_collection().find({})
        else:
            cursor = self.get_collection().find({"$or": [
            {"_id": _id},
            {"_id": ObjectId(_id)}
        ]})

        result_list = []
        for result in cursor:
            result["_id"] = str(result["_id"])
            result["original_id"] = str(result["original_id"])
            result_list.append(result)

        if not result_list:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return result_list


    def get_sub_class(self, _id: str):
        """
        查詢指定 main_class 下的所有 sub_classes
        """

        sub_class_list = []

        if _id == "all":
            result = self.get_collection().find({})
            for document in result:
                for sub in document["sub_classes"]:  # 這裡展開 `sub_classes`
                    sub_class_list.append(
                        {
                            "_id": str(document["_id"]),  # 轉換 `_id` 為字串
                            "original_id": str(document["original_id"]),  # 轉換 `original_id` 為字串
                            "name": document["name"],
                            "sub_class": sub["sub_class"],  # 只回傳 `sub_class` 屬性
                        }
                    )

        else:
            try:
                object_id = ObjectId(_id)  # 嘗試轉換 `_id` 為 `ObjectId`
            except:
                object_id = _id  # 如果轉換失敗，就用字串查詢

            result = self.get_collection().find({"_id": object_id})
            for document in result:
                for sub in document["sub_classes"]:
                    sub_class_list.append(
                        {
                            "_id": str(document["_id"]),
                            "original_id": str(document["original_id"]),
                            "name": document["name"],
                            "sub_class": sub["sub_class"],
                        }
                    )

        if not sub_class_list:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return sub_class_list

    
    def get_option_class(self, _id: str, sub_class: str):
        option_class_list = []

        query = {"_id": ObjectId(_id)} if _id != "all" else {}
        # print(f"查詢條件: {query}")  # 🛠 檢查 MongoDB 查詢條件

        # ✅ 修正：先存成 list 避免游標被消耗
        result_cursor = self.get_collection().find(query)
        result_list = list(result_cursor)

        # print(f"查詢結果: {result_list}")  # 🛠 確保 MongoDB 查詢有資料

        for document in result_list:  # ✅ 改用 result_list
            for sub in document.get("sub_classes", []):
                # print(f"目前處理的 sub_class: {sub['sub_class']}")
                
                # ✅ 修正：使用 .strip() 避免空格影響匹配
                if sub_class.strip() == "all" or sub["sub_class"].strip() == sub_class.strip():
                    # print(f"匹配的 sub_class: {sub['sub_class']}")  # ✅ 確保進入匹配條件
                    option_class_list.append({
                        "sub_class": sub["sub_class"],
                        "option_class": sub.get("option_class", [])
                    })

        print(f"最後回傳的選項: {option_class_list}")  # 🛠 確保有匹配到資料
        return option_class_list




