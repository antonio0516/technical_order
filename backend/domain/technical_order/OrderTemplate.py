import datetime

from bson.objectid import ObjectId
from fastapi import HTTPException

from domain.database.database import mongo_database


class OrderTemplate:
    def __init__(self):
        self._order_template_column_type_list = [
            "text",
            "file-multiple",
            "select",
            "select-multiple",
        ]
        self.DEFAULT_ORDER_TEMPLATE_COLUMN = [
            {
                "name": "主目錄",
                "type": "select",
            },
            {
                "name": "次目錄",
                "type": "select",
            },
            {
                "name": "輔助圖片",
                "type": "file-multiple",
            },
            {
                "name": "輔助影片",
                "type": "file-multiple",
            },
            {
                "name": "輔助 PDF",
                "type": "file-multiple",
            },
            {
                "name": "標籤",
                "type": "select-multiple",
            },
            {
                "name": "step 步驟",
                "type": "text",
            },
            {
                "name": "步驟名稱",
                "type": "text",
            },
            {
                "name": "說明描述",
                "type": "text",
            },
        ]

    def get_order_template_column(self, order_template_column_id: str):
        # check if order_template_column already exists
        result = self.get_order_template_column_collection().find_one(
            {"_id": ObjectId(order_template_column_id)}
        )
        if result is None:
            raise HTTPException(status_code=409, detail="欄位不存在")

        return result

    def reset_default_order_template_column(self):
        # clear all order_template_column
        self.get_order_template_column_collection().delete_many({})
        # add default order_template_column
        for order_template_column in self.DEFAULT_ORDER_TEMPLATE_COLUMN:
            self.add_order_template_column(order_template_column)

    def get_order_template_column_collection(self):
        return mongo_database["technical_order_order_template_column"]

    def add_order_template_column(self, order_template: dict):
        """
        TODO: validate order_template_column format
        """

        """
        Check if type in column_type
        """
        column_type_list = self.get_all_order_template_column_type()
        if order_template["type"] not in column_type_list:
            raise HTTPException(status_code=409, detail="欄位類型不存在")

        """
        Check if order_template_column already exists
        """
        order_template_list = self.get_order_template_column_collection().find({})
        order_template_list = [
            order_template["name"] for order_template in order_template_list
        ]
        if order_template["name"] in order_template_list:
            raise HTTPException(status_code=409, detail="欄位已存在")

        data = {
            "name": order_template["name"],
            "type": order_template["type"],
            "created_at": datetime.datetime.now(),
        }

        try:
            self.get_order_template_column_collection().insert_one(data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="新增失敗")

    def get_all_order_template_column(self):
        """
        TODO: validate order_template_column format
        """

        result = self.get_order_template_column_collection().find({})
        order_template_column_list = []

        for document in result:
            order_template_column_list.append(document)

        # change id to string
        for order_template_column in order_template_column_list:
            order_template_column["_id"] = str(order_template_column["_id"])

        return order_template_column_list

    def update_order_template_column_name(
        self, order_template_column_id: str, new_column_name: str
    ):
        """
        TODO: validate order_template_column format
        """

        """
        Check if order_template_column already exists
        """
        result = self.get_order_template_column_collection().find_one(
            {"_id": ObjectId(order_template_column_id)}
        )
        if result is None:
            raise HTTPException(status_code=409, detail="欄位不存在")

        data = result
        data["name"] = new_column_name

        try:
            self.get_order_template_column_collection().replace_one(
                {"_id": ObjectId(order_template_column_id)}, data
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="更新失敗")

    def delete_order_template_column(self, order_template_column_id: str):
        """
        TODO: validate order_template_column format
        """

        """
        Check if order_template_column already exists
        """

        # change str to ObjectId
        result = self.get_order_template_column_collection().find_one(
            {"_id": ObjectId(order_template_column_id)}
        )
        if result is None:
            raise HTTPException(status_code=409, detail="欄位不存在")

        try:
            self.get_order_template_column_collection().delete_one(
                {"_id": ObjectId(order_template_column_id)}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="刪除失敗")

    """
    For order template column type
    """

    def get_all_order_template_column_type(self):
        """
        TODO: validate order_template_column format
        """

        return self._order_template_column_type_list
