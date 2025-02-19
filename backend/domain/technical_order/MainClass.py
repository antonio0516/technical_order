import datetime
import traceback

from bson.objectid import ObjectId
from fastapi import HTTPException

from domain.database.database import mongo_client, mongo_database
from domain.technical_order.Order import Order


class MainClass:
    def __init__(self):
        pass

    def get_collection(self):
        return mongo_database["technical_order_main_class"]

    def add(self, main_class: str):
        """
        TODO: validate main_class format
        """

        """
        Check if main_class already exists
        """
        result = self.get_collection().find_one({"name": main_class})
        if result is not None:
            raise HTTPException(status_code=409, detail="主目錄已存在")

        data = {
            "name": main_class,
            "sub_class": [],
            "created_at": datetime.datetime.now(),
        }

        try:
            self.get_collection().insert_one(data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="新增失敗")

    def get(self, main_class_id: int):
        """
        TODO: validate main_class format
        """

        """
        Check if main_class already exists
        """
        result = self.get_collection().find_one({"_id": ObjectId(main_class_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return result

    def get_all(self):
        cursor = self.get_collection().find({})
        main_class_list = []

        for document in cursor:
            main_class_list.append(document)

        # change if to string
        for main_class in main_class_list:
            main_class["_id"] = str(main_class["_id"])

        return main_class_list

    def update_name(self, main_class_id: str, main_class: str):
        """
        TODO: validate main_class format
        """

        """
        Check if main_class already exists
        """
        result = self.get_collection().find_one({"_id": ObjectId(main_class_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        data = result
        data["name"] = main_class

        try:
            self.get_collection().replace_one({"_id": ObjectId(main_class_id)}, data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="更新失敗")

    def delete(self, main_class_id: str):
        """
        TODO: validate main_class format
        """

        """
        Check if main_class already exists
        """
        # change str to ObjectId
        print(main_class_id)
        result = self.get_collection().find_one({"_id": ObjectId(main_class_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")
        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    """
                    remove all orders with this main_class
                    """
                    order = Order()
                    order_collection = order.get_order_collection()   #mongo_db.technical_order mongo_db["technical_order"] 差別
                    # find all orders with this main_class
                    result = order_collection.find({"mainClass": str(main_class_id)})
                    for document in result:
                        order.delete_technical_order(
                            str(document["_id"]), external_session=session
                        )
                    """
                    remove main_class
                    """
                    self.get_collection().delete_one(
                        {"_id": ObjectId(main_class_id)}, session=session
                    )
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="刪除失敗")

    """
    For sub classes
    """

    def get_sub_classes(self, main_class_id: str):
        """
        TODO: validate main_class format
        """

        sub_class_list = []

        """
        Check if main_class already exists
        """
        if main_class_id == "all":
            result = self.get_collection().find({})
            for document in result:
                for sub_class in document["sub_class"]:
                    sub_class_list.append(
                        {
                            "main_class": document["name"],
                            "sub_class": sub_class,
                            "main_class_id": str(document["_id"]),
                        }
                    )

        else:
            result = self.get_collection().find_one({"_id": ObjectId(main_class_id)})
            for sub_class in result["sub_class"]:
                sub_class_list.append(
                    {
                        "main_class": result["name"],
                        "sub_class": sub_class,
                        "main_class_id": str(result["_id"]),
                    }
                )

        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        return sub_class_list

    def add_sub_class(self, main_class_id: str, sub_class: str):
        """
        TODO: validate sub_class format
        """

        """
        Check if main class already exists
        """
        result = self.get_collection().find_one({"_id": ObjectId(main_class_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        """
        Check if sub_class already exists
        """
        if sub_class in result["sub_class"]:
            raise HTTPException(status_code=409, detail="次目錄已存在")

        data = result
        data["sub_class"].append(sub_class)

        try:
            self.get_collection().replace_one({"_id": ObjectId(result["_id"])}, data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="新增失敗")

    def delete_sub_class(self, main_class_id: str, sub_class: str):
        """
        TODO: validate sub_class format
        """

        """
        Check if main class already exists
        """
        result = self.get_collection().find_one({"_id": ObjectId(main_class_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        """
        Check if sub_class already exists
        """
        if sub_class not in result["sub_class"]:
            raise HTTPException(status_code=409, detail="次目錄不存在")

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    """
                    remove all orders with this sub_class
                    """
                    order = Order()
                    order_collection = order.get_order_collection()
                    # find all orders with this sub_class
                    result = order_collection.find(
                        {"mainClass": str(main_class_id), "subClass": sub_class}
                    )
                    for document in result:
                        order.delete_technical_order(
                            str(document["_id"]), external_session=session
                        )

                    """
                    remove sub_class
                    """
                    result = self.get_collection().find_one(
                        {"_id": ObjectId(main_class_id)}
                    )
                    data = result
                    data["sub_class"].remove(sub_class)
                    self.get_collection().replace_one(
                        {"_id": ObjectId(result["_id"])}, data, session=session
                    )
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="刪除失敗")

    def update_sub_class(
        self, main_class_id: str, old_sub_class: str, new_sub_class: str
    ):
        """
        TODO: validate sub_class format
        """

        """
        Check if main class already exists
        """
        result = self.get_collection().find_one({"_id": ObjectId(main_class_id)})
        if result is None:
            raise HTTPException(status_code=409, detail="主目錄不存在")

        """
        Check if old sub_class already exists
        """
        if old_sub_class not in result["sub_class"]:
            raise HTTPException(status_code=409, detail="舊的次目錄不存在")

        """
        Check if new sub_class already exists
        """
        if new_sub_class in result["sub_class"]:
            raise HTTPException(status_code=409, detail="新的次目錄已存在")

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    """
                    update sub_class
                    """
                    result = self.get_collection().find_one(
                        {"_id": ObjectId(main_class_id)}
                    )
                    data = result
                    data["sub_class"].remove(old_sub_class)
                    data["sub_class"].append(new_sub_class)
                    self.get_collection().replace_one(
                        {"_id": ObjectId(result["_id"])}, data, session=session
                    )

                    """
                    update all orders with this sub_class
                    """
                    order = Order()
                    order_collection = order.get_order_collection()
                    order_collection.update_many(
                        {"mainClass": str(main_class_id), "subClass": old_sub_class},
                        {"$set": {"subClass": new_sub_class}},
                        session=session,
                    )
        except Exception as e:
            raise HTTPException(status_code=500, detail="更新失敗")
