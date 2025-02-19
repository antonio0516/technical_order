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
    

    def get_original_main_class(self, original_id: str):
        """
        根據 original_id 查詢所有符合的資料
        """
        cursor = self.get_collection().find({"original_id": ObjectId(original_id)})

        result_list = []
        for result in cursor:
            result["_id"] = str(result["_id"])
            result["original_id"] = str(result["original_id"])
            result_list.append(result)

        if not result_list:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return result_list


    def get_original_sub_class(self, original_id: str):
        """
        TODO: validate main_class format
        """

        sub_class_list = []

        """
        Check if main_class already exists
        """
        if original_id == "all":
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

            result = self.get_collection().find({"original_id": ObjectId(original_id)})
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
    
    def get_original_option_class(self, original_id: str, sub_class: str):
        """
        TODO: validate main_class format
        """

        option_class_list = []

        """
        Check if main_class already exists
        """
        if original_id == "all":
            result = self.get_collection().find({})
            if sub_class == 'all':
                for document in result:
                    for options in document["option_class"]:
                        option_class_list.append(
                        {
                            "sub_class": document["sub_class"],
                            "option_class": options,
                        }
                    )
            else:
                target = self.get_collection().find({"sub_class": sub_class})
                for document in target:
                    for options in document["option_class"]:
                        option_class_list.append(
                            {
                                "name": document["name"],
                                "sub_class": document["sub_class"],
                                "option_class": options,
                            }
                        )

        else:
            result = self.get_collection().find({"original_id": ObjectId(original_id)})
            if sub_class == 'all':
                for document in result:
                    for options in document["option_class"]:
                        option_class_list.append(
                        {
                            "sub_class": document["sub_class"],
                            "option_class": options,
                        }
                    )
            else:
                for document in result:
                    if document["sub_class"] == sub_class:
                        break
                for options in document["option_class"]:
                    option_class_list.append(
                            {
                                "name": document["name"],
                                "sub_class": document["sub_class"],
                                "option_class": options,
                            }
                    )

        return option_class_list
    