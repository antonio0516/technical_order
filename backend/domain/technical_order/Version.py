import datetime
import json
import os
import shutil
import traceback
from typing import List

from bson.objectid import ObjectId
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from domain.database.database import mongo_client, mongo_database
from domain.tmp_folder import TmpFolder


class Version:
    def __init__(self):
        # self.COLLECTION_LIST = [
        #     "order_upload_file",
        #     "student",
        #     "technical_order",
        #     "technical_order_main_class",
        #     "technical_order_order_template_column",
        # ]
        pass

    def get_collection_list_exclude_common(self):
        collection_list = mongo_database.list_collection_names()
        collection_list.remove("technical_order_version")
        collection_list.remove("admin_log")
        return collection_list

    def get_version_collection(self):
        return mongo_database.technical_order_version

    def get_store_version_path(self):
        return "./versions"

    def get_storage_path(self):
        return "./storage"

    def get_all_version(self):
        return self.get_version_collection().find({"deleted_flag": {"$ne": True}})

    def get_version_by_id(self, id: str):
        return self.get_version_collection().find_one({"_id": ObjectId(id)})

    def save_current_version(self, version_name: str):
        version = {
            "version_name": version_name,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        # check if version_name already exists
        if (
            self.get_version_collection().find_one({"version_name": version_name})
            is not None
        ):
            raise HTTPException(status_code=409, detail="版本名稱已存在")

        folder_path = ""

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # insert into collection
                    version["_id"] = ObjectId()
                    version_id = version["_id"]
                    self.get_version_collection().insert_one(version, session=session)

                    # save all collection into a file
                    folder_path = self.get_store_version_path() + "/" + str(version_id)

                    # create folder
                    os.makedirs(folder_path)
                    # save all collection into a file
                    for collection in self.get_collection_list_exclude_common():
                        file_path = folder_path + "/" + collection + ".json"
                        data = list(mongo_database[collection].find())
                        with open(file_path, "w") as file:
                            json.dump(data, file, default=str)

                    # copy storage folder into the version folder's storage folder
                    storage_path = self.get_storage_path()
                    version_storage_path = folder_path + "/storage"
                    os.makedirs(version_storage_path)
                    for root, dirs, files in os.walk(storage_path):
                        for file in files:
                            shutil.copy(os.path.join(root, file), version_storage_path)
        except Exception as e:
            # if folder is exist, delete it
            if folder_path != "" and os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="新增失敗")

    def remove_version_completely(self, id: str):
        doc = self.get_version_collection().find_one({"_id": ObjectId(id)})
        if doc is None:
            return

        if os.path.exists(self.get_store_version_path() + "/" + id):
            shutil.rmtree(self.get_store_version_path() + "/" + id)
        self.get_version_collection().delete_one({"_id": ObjectId(id)})

    def delete_version_by_id(self, id: str):
        version = self.get_version_collection().find_one({"_id": ObjectId(id)})
        if version is None:
            raise HTTPException(status_code=404, detail="版本不存在")

        try:
            # delete all collection
            folder_path = self.get_store_version_path() + "/" + id
            self.get_version_collection().update_one(
                {"_id": ObjectId(id)},
                {"$set": {"deleted_flag": True}},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="刪除失敗")

    def restore_version_by_id(self, id: str):
        version = self.get_version_collection().find_one({"_id": ObjectId(id)})
        if version is None:
            raise HTTPException(status_code=404, detail="版本不存在")

        backup_flag = False

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # delete all collection
                    for collection in self.get_collection_list_exclude_common():
                        file_path = (
                            self.get_store_version_path()
                            + "/"
                            + id
                            + "/"
                            + collection
                            + ".json"
                        )
                        with open(file_path, "r") as file:
                            data = json.load(file)
                            mongo_database[collection].delete_many({}, session=session)
                            # prevent empty data
                            if len(data) == 0:
                                continue
                            # change _id from string to ObjectId
                            for item in data:
                                if "_id" in item:
                                    item["_id"] = ObjectId(item["_id"])
                            mongo_database[collection].insert_many(
                                data, session=session
                            )

                    # delete storage folder
                    backup_flag = False
                    TmpFolder.clear_folder()
                    TmpFolder.backup_folder(self.get_storage_path())
                    backup_flag = True

                    storage_path = self.get_storage_path()
                    version_storage_path = (
                        self.get_store_version_path() + "/" + id + "/storage"
                    )
                    shutil.rmtree(storage_path)
                    os.makedirs(storage_path)
                    # copy version storage folder into the storage folder
                    for root, dirs, files in os.walk(version_storage_path):
                        for file in files:
                            shutil.copy(os.path.join(root, file), storage_path)
        except Exception as e:
            traceback.print_exc()
            # if storage folder is not exist, create it
            storage_path = self.get_storage_path()
            if not os.path.exists(storage_path):
                os.makedirs(storage_path)

            if backup_flag:
                TmpFolder.restore_folder(self.get_storage_path())

            raise HTTPException(status_code=500, detail="還原失敗")
