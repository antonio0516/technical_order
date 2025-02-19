import datetime
import traceback

from bson.objectid import ObjectId
from fastapi import HTTPException

from domain.database.database import mongo_client, mongo_database
from domain.technical_order.Order import Order


class Tag:
    def __init__(self):
        pass

    def get_collection(self):
        return mongo_database["technical_order_tag"]

    def add(self, tag: str):
        """
        TODO: validate tag format
        """

        """
        Check if tag already exists
        """
        result = self.get_collection().find_one({"name": tag})
        if result is not None:
            raise HTTPException(status_code=409, detail="標籤已存在")

        data = {
            "name": tag,
            "created_at": datetime.datetime.now(),
        }

        try:
            self.get_collection().insert_one(data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="新增失敗")

    def get(self, tag_id: int):
        """
        TODO: validate tag format
        """

        """
        Check if tag already exists
        """
        result = self.get_collection().find_one({"_id": ObjectId(tag_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="標籤不存在")

        return result

    def get_all(self):
        cursor = self.get_collection().find({})
        tag_list = []

        for document in cursor:
            tag_list.append(document)

        # change if to string
        for tag in tag_list:
            tag["_id"] = str(tag["_id"])

        return tag_list

    def update_name(self, tag_id: str, tag: str):
        """
        TODO: validate tag format
        """

        """
        Check if tag already exists
        """
        result = self.get_collection().find_one({"_id": ObjectId(tag_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="標籤不存在")

        data = result
        data["name"] = tag

        try:
            self.get_collection().replace_one({"_id": ObjectId(tag_id)}, data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="更新失敗")

    def delete(self, tag_id: str):
        """
        TODO: validate tag format
        """

        """
        Check if tag already exists
        """
        # change str to ObjectId
        result = self.get_collection().find_one({"_id": ObjectId(tag_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="標籤不存在")

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    """
                    Remove tag from order
                    """
                    order = Order()
                    order_collection = order.get_order_collection()
                    order_collection.update_many(
                        {}, {"$pull": {"tags": str(tag_id)}}, session=session
                    )
                    """
                    remove tag
                    """
                    self.get_collection().delete_one(
                        {"_id": ObjectId(tag_id)}, session=session
                    )
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="刪除失敗")
