import datetime
import traceback

from bson.objectid import ObjectId
from fastapi import HTTPException

from domain.database.database import mongo_client, mongo_database
from domain.technical_order.Order import Order

class OptionClass:
    def __init__(self):
        pass
    def get_collection(self):
        return mongo_database["db_for_subclass"]
    def get_all(self):
        """
        TODO: validate main_class format
        """

        """
        Check if main_class already exists
        """
        result = self.get_collection().find({})
        result_list = []
        
        for inside in result:
            inside["original_id"] = str(inside["original_id"])
            inside["_id"] = str(inside["_id"])
            result_list.append(inside)
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return result_list


    def get_original_main_class(self, _id: str):
        """
        根據 original_id 查詢所有符合的資料
        """
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


    def get_original_sub_class(self, _id: str):
        """
        TODO: validate main_class format
        """

        sub_class_list = []

        """
        Check if main_class already exists
        """
        if _id == "all":
            result = self.get_collection().find({})
            for document in result:
                sub_class_list.append(
                    {
                        "name": document["name"],
                        "sub_class": document["sub_class"],
                        "original_id": str(document["original_id"])
                    }
                )

        else:

            result = self.get_collection().find({"_id": ObjectId(_id)})
            for document in result:
                sub_class_list.append(
                    {
                            "name": document["name"],
                            "sub_class": document["sub_class"],
                            "original_id": str(document["original_id"])
                    }
                )

        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return sub_class_list
    
    def get_original_option_class(self, _id: str, sub_class: str):
        option_class_list = []


        query = {}
        if _id != "all":
            try:
                query["_id"] = ObjectId(_id)
            except Exception:
                query["_id"] = _id  # 如果不是 ObjectId 就直接當字串查詢

        if sub_class != "all":
            query["sub_class"] = sub_class

        result = self.get_collection().find(query)

        for document in result:
            option_classes = document.get("option_class", [])
            for option in option_classes:
                option_class_list.append(
                    {
                        "sub_class": document.get("sub_class", ""),
                        "option_class": option,
                    }
                )
        print("!")
        print(option_class_list)
        print("")
        return option_class_list
