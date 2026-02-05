import glob
import os
import re
import shutil
import traceback
from copy import deepcopy
from typing import List

import psutil
from bson.objectid import ObjectId
from starlette.datastructures import UploadFile

from domain.database.database import mongo_client, mongo_database


class Order:
    FILE_SIZE_LIMIT = 100 * 1024 * 1024
    PAGE_LIMIT = 20
    SORT_COLUMN = [
        ("mainClass", 1),
        ("subClass", 1),
        ("optionClass",1),
        ("sort_tags", 1),
        ("sort_step_number", 1),
        ("_id", 1),
    ]

    def __init__(self):
        pass

    def get_order_collection(self):
        return mongo_database.technical_order
    
    #### 2025/02/26 ####
    def get_new_order_collection(self):
        return mongo_database.new_technical_order
    ####------------####
    def get_order_upload_file_collection(self):
        return mongo_database.order_upload_file

    def get_upload_file(self, id: str):
        return self.get_order_upload_file_collection().find_one({"_id": ObjectId(id)})

    def _extract_and_format_numbers(self, input_str):
        numbers = re.findall(r"\d+", input_str)
        formatted_numbers = [f"{int(num):04}" for num in numbers]
        result = ".".join(formatted_numbers)
        return result

    def _add_sort_columns(self, request_data):
        sort_tags = sorted(request_data["tags"])
        sort_tags = ",".join(sort_tags)
        request_data["sort_tags"] = sort_tags

        step_number = request_data["stepNumber"]

        if step_number == "":
            request_data["sort_step_number"] = ""
        else:
            formatted_step_number = self._extract_and_format_numbers(step_number)
            request_data["sort_step_number"] = formatted_step_number
        return request_data

    def add_technical_order(
        self,
        image_list: List[UploadFile],
        video_list: List[UploadFile],
        pdf_list: List[UploadFile],
        old_db_data,  # 舊資料庫用的資料 (合併後的 subClass)
        new_db_data,  # 新資料庫用的資料 (分離的 subClass 和 optionClass)
    ):
        """
        同時寫入舊資料庫和新資料庫
        TODO: validate technical_order format
        """
        image_id_list = []
        video_id_list = []
        pdf_id_list = []

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # 處理檔案上傳 (圖片、影片、PDF)
                    for image in image_list:
                        image_data = {
                            "file_name": image.filename,
                            "type": "image",
                            "extension": image.filename.split(".")[-1],
                        }

                        id = ObjectId()
                        image_data["_id"] = id
                        id = str(id)
                        self.get_order_upload_file_collection().insert_one(
                            image_data, session=session
                        )

                        # save image_list, video_list in local storage
                        with open(
                            f"./storage/{id}.{image_data['extension']}", "wb"
                        ) as f:
                            f.write(image.file.read())

                        image_id_list.append(id)

                    for video in video_list:
                        video_data = {
                            "file_name": video.filename,
                            "type": "video",
                            "extension": video.filename.split(".")[-1],
                        }
                        id = ObjectId()
                        video_data["_id"] = id
                        id = str(id)
                        self.get_order_upload_file_collection().insert_one(
                            video_data, session=session
                        )

                        # save image_list, video_list in local storage
                        with open(
                            f"./storage/{id}.{video_data['extension']}", "wb"
                        ) as f:
                            f.write(video.file.read())

                        video_id_list.append(id)

                    for pdf in pdf_list:
                        pdf_data = {
                            "file_name": pdf.filename,
                            "type": "pdf",
                            "extension": pdf.filename.split(".")[-1],
                        }
                        id = ObjectId()
                        pdf_data["_id"] = id
                        id = str(id)
                        self.get_order_upload_file_collection().insert_one(
                            pdf_data, session=session
                        )

                        # save image_list, video_list in local storage
                        with open(f"./storage/{id}.{pdf_data['extension']}", "wb") as f:
                            f.write(pdf.file.read())

                        pdf_id_list.append(id)

                    # 為兩個資料庫準備檔案ID列表
                    file_ids = {
                        "image_id_list": image_id_list,
                        "video_id_list": video_id_list,
                        "pdf_id_list": pdf_id_list
                    }

                    # 寫入舊資料庫 (technical_order)
                    old_db_data.update(file_ids)
                    old_db_data = self._add_sort_columns(old_db_data)
                    self.get_order_collection().insert_one(
                        old_db_data, session=session
                    )

                    # 寫入新資料庫 (new_technical_order)  
                    new_db_data.update(file_ids)
                    new_db_data = self._add_sort_columns(new_db_data)
                    self.get_new_order_collection().insert_one(
                        new_db_data, session=session
                    )

        except Exception as e:
            # remove image_list, video_list in local storage
            merge_list = image_id_list + video_id_list + pdf_id_list
            for f in os.listdir("./storage"):
                if f.split(".")[0] in merge_list:
                    os.remove(f"./storage/{f}")
            print(f"新增技令異常: {str(e)}")
            traceback.print_exc()
            raise Exception("Technical Order Insertion Failed")

    def duplicate_technical_order(self, technical_order_id: str):
        new_file_id_list = []   
        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # 🔧 從舊資料庫取得技令資料
                    old_result = self.get_order_collection().find_one(
                        {"_id": ObjectId(technical_order_id)}
                    )
                    
                    # 🔧 檢查新資料庫是否有對應資料
                    new_result = self.get_new_order_collection().find_one(
                        {"_id": ObjectId(technical_order_id)}
                    )

                    if old_result is None and new_result is None:
                        raise Exception("找不到要複製的技令")

                    # 🔧 決定使用哪個來源資料
                    source_result = old_result if old_result else new_result
                    original_result = deepcopy(source_result)
                    
                    print(f"🔧 開始複製技令: {source_result.get('stepName', 'Unknown')}")
                    
                    file_columns = ["image_id_list", "video_id_list", "pdf_id_list"]

                    # 🔧 複製檔案並建立映射
                    file_id_mapping = {}
                    for file_column in file_columns:
                        if file_column in original_result and original_result[file_column]:
                            for file_id in original_result[file_column]:
                                if file_id not in file_id_mapping:
                                    file = self.get_upload_file(file_id)
                                    if file is None:
                                        print(f"⚠️  找不到檔案: {file_id}")
                                        continue
                                        
                                    file_copy = deepcopy(file)
                                    file_copy.pop("_id")
                                    new_file_id = ObjectId()
                                    file_copy["_id"] = new_file_id
                                    self.get_order_upload_file_collection().insert_one(file_copy, session=session)

                                    # 複製實體檔案
                                    new_file_id_str = str(new_file_id)
                                    new_file_id_list.append(new_file_id_str)
                                    file_id_mapping[file_id] = new_file_id_str
                                    
                                    # 檢查原始檔案是否存在
                                    original_file_path = f"./storage/{file_id}.{file['extension']}"
                                    new_file_path = f"./storage/{new_file_id_str}.{file['extension']}"
                                    
                                    if os.path.exists(original_file_path):
                                        shutil.copy(original_file_path, new_file_path)
                                        print(f"✅ 複製檔案: {original_file_path} -> {new_file_path}")
                                    else:
                                        print(f"⚠️  原始檔案不存在: {original_file_path}")


                    old_duplicate = deepcopy(source_result)
                    old_duplicate.pop("_id")
                    
                    if old_result:
                        # 如果來源是舊資料庫，保持原有格式
                        pass  # 已經是合併格式
                    else:
                        # 如果來源是新資料庫，需要合併 subClass 和 optionClass
                        sub_class = source_result.get("subClass", "")
                        option_class = source_result.get("optionClass", "")
                        
                        if option_class and sub_class:
                            old_duplicate["subClass"] = f"{sub_class} - {option_class}"
                        elif sub_class:
                            old_duplicate["subClass"] = sub_class
                        
                        # 🔧 移除 optionClass（舊資料庫不需要）
                        if "optionClass" in old_duplicate:
                            old_duplicate.pop("optionClass")
                    
                    # 更新檔案ID
                    for column in file_columns:
                        if column in old_duplicate and old_duplicate[column]:
                            old_duplicate[column] = [file_id_mapping.get(file_id, file_id) for file_id in old_duplicate[column]]
                    
                    new_old_id = ObjectId()
                    old_duplicate["_id"] = new_old_id
                    self.get_order_collection().insert_one(old_duplicate, session=session)

                 
                    if new_result is not None:
                        # 如果新資料庫中有對應資料，使用新版本
                        new_duplicate = deepcopy(new_result)
                    else:
                        # 如果新資料庫中沒有對應資料，從來源轉換
                        new_duplicate = deepcopy(source_result)
                        
                        if old_result:
                            # 如果來源是舊資料庫，需要分離合併的 subClass
                            if "subClass" in new_duplicate and isinstance(new_duplicate["subClass"], str) and " - " in new_duplicate["subClass"]:
                                parts = new_duplicate["subClass"].split(" - ")
                                new_duplicate["subClass"] = parts[0]
                                new_duplicate["optionClass"] = parts[1] if len(parts) > 1 else ""
                            else:
                                if "optionClass" not in new_duplicate:
                                    new_duplicate["optionClass"] = ""
                        else:
                            # 如果來源是新資料庫，保持原有的分離格式
                            pass

                    new_duplicate.pop("_id")
                    
                    # 更新檔案ID
                    for column in file_columns:
                        if column in new_duplicate and new_duplicate[column]:
                            new_duplicate[column] = [file_id_mapping.get(file_id, file_id) for file_id in new_duplicate[column]]
                    
                    new_new_id = ObjectId()
                    new_duplicate["_id"] = new_new_id
                    self.get_new_order_collection().insert_one(new_duplicate, session=session)
                    print("✅ 已寫入新資料庫")
                    
                    print(f"🎉 技令複製完成，新的 old_id: {new_old_id}, 新的 new_id: {new_new_id}")

        except Exception as e:
            # 清理已複製的檔案
            print(f"❌ 複製過程發生錯誤: {str(e)}")
            for f in os.listdir("./storage"):
                if f.split(".")[0] in new_file_id_list:
                    try:
                        os.remove(f"./storage/{f}")
                        print(f"🗑️  清理檔案: {f}")
                    except:
                        pass
            traceback.print_exc()
            raise Exception(f"Technical Order Duplication Failed: {str(e)}")

    def get_technical_order(
        self,
        technical_order_id=None,
        main_class=None,
        sub_class=None,
        option_class=None,
        page_mode=None,
        last_id=None,
    ):
        if technical_order_id is not None:
            return self.get_order_collection().find_one(
                {"_id": ObjectId(technical_order_id)}
            )

        elif sub_class is not None and main_class is not None:
            if page_mode is not None:
                if last_id is None:
                    return (
                        self.get_order_collection()
                        .find({"mainClass": main_class, "subClass": sub_class})
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
                if last_id is not None:
                    # get sort column info of last_id
                    last_order = self.get_order_collection().find_one(
                        {"_id": ObjectId(last_id)}
                    )
                    return (
                        self.get_order_collection()
                        .find(
                            {
                                "mainClass": main_class,
                                "subClass": sub_class,
                                "$or": [
                                    {
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": last_order[
                                            "sort_step_number"
                                        ],
                                        "_id": {"$gt": ObjectId(last_id)},
                                    },
                                    {
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": {
                                            "$gt": last_order["sort_step_number"]
                                        },
                                    },
                                    {"sort_tags": {"$gt": last_order["sort_tags"]}},
                                ],
                            }
                        )
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
            return self.get_order_collection().find(
                {"mainClass": main_class, "subClass": sub_class}
            )

        elif main_class is not None:
            if page_mode is not None:
                if last_id is None:
                    return (
                        self.get_order_collection()
                        .find({"mainClass": main_class})
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
                if last_id is not None:
                    last_order = self.get_order_collection().find_one(
                        {"_id": ObjectId(last_id)}
                    )
                    return (
                        self.get_order_collection()
                        .find(
                            {
                                "mainClass": main_class,
                                "$or": [
                                    {
                                        "subClass": last_order["subClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": last_order[
                                            "sort_step_number"
                                        ],
                                        "_id": {"$gt": ObjectId(last_id)},
                                    },
                                    {
                                        "subClass": last_order["subClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": {
                                            "$gt": last_order["sort_step_number"]
                                        },
                                    },
                                    {
                                        "subClass": last_order["subClass"],
                                        "sort_tags": {"$gt": last_order["sort_tags"]},
                                    },
                                    {
                                        "subClass": {"$gt": last_order["subClass"]},
                                    },
                                ],
                            }
                        )
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
            return self.get_order_collection().find({"mainClass": main_class})

        else:
            if page_mode is not None:
                if last_id is None:
                    return (
                        self.get_order_collection()
                        .find({})
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
                if last_id is not None:
                    last_order = self.get_order_collection().find_one(
                        {"_id": ObjectId(last_id)}
                    )
                    return (
                        self.get_order_collection()
                        .find(
                            {
                                "$or": [
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": last_order["subClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": last_order[
                                            "sort_step_number"
                                        ],
                                        "_id": {"$gt": ObjectId(last_id)},
                                    },
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": last_order["subClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": {
                                            "$gt": last_order["sort_step_number"]
                                        },
                                    },
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": last_order["subClass"],
                                        "sort_tags": {"$gt": last_order["sort_tags"]},
                                    },
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": {"$gt": last_order["subClass"]},
                                    },
                                    {"mainClass": {"$gt": last_order["mainClass"]}},
                                ]
                            }
                        )
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
            return self.get_order_collection().find({})

        

    def remove_order_file_completely(self, file_id: str):
        doc = self.get_order_upload_file_collection().find_one(
            {"_id": ObjectId(file_id)}
        )
        if doc is None:
            return
        extension = doc["extension"]

        # check if file exists
        if os.path.exists(f"./storage/{file_id}.{extension}"):
            os.remove(f"./storage/{file_id}.{extension}")
        self.get_order_upload_file_collection().delete_one({"_id": ObjectId(file_id)})

    def delete_order_file(self, file_id: str, session=None):
        # add delete flag
        self.get_order_upload_file_collection().update_one(
            {"_id": ObjectId(file_id)}, {"$set": {"delete_flag": True}}, session=session
        )

    def delete_technical_order(self, technical_order_id: str, external_session=None):
        #  先嘗試用 ID 找到要刪除的技令（作為主要來源）
        old_result = self.get_order_collection().find_one(
            {"_id": ObjectId(technical_order_id)}
        )
        
        new_result = self.get_new_order_collection().find_one(
            {"_id": ObjectId(technical_order_id)}
        )

        #  如果用 ID 找不到，就用內容比對的方式
        if old_result is None and new_result is None:
            print(f"  用 ID 找不到技令，嘗試用內容比對...")
            raise Exception("找不到要刪除的技令")
        
        #  決定主要刪除目標和需要比對刪除的目標
        primary_result = old_result if old_result else new_result
        primary_db = "舊" if old_result else "新"
        
        print(f" 主要刪除目標: {primary_db}資料庫的技令 - {primary_result['stepName']}")

        #  收集檔案ID
        all_file_ids = set()
        all_file_ids.update(primary_result.get("image_id_list", []))
        all_file_ids.update(primary_result.get("video_id_list", []))
        all_file_ids.update(primary_result.get("pdf_id_list", []))

        # 🔧 如果只有一個資料庫有資料，需要找到另一個資料庫的對應資料
        corresponding_result = None
        corresponding_id = None
        
        if old_result and not new_result:
            # 舊資料庫有，新資料庫沒有 → 用舊資料庫的 subClass 去新資料庫找
            old_sub_class = old_result.get("subClass", "")
            if " - " in old_sub_class:
                parts = old_sub_class.split(" - ")
                search_sub_class = parts[0]
                search_option_class = parts[1] if len(parts) > 1 else ""
            else:
                search_sub_class = old_sub_class
                search_option_class = ""
            
            # 在新資料庫中搜尋匹配的技令
            corresponding_result = self.get_new_order_collection().find_one({
                "stepName": primary_result["stepName"],
                "stepNumber": primary_result["stepNumber"],
                "mainClass": primary_result["mainClass"],
                "subClass": search_sub_class,
                "optionClass": search_option_class
            })
            
            if corresponding_result:
                corresponding_id = corresponding_result["_id"]
                print(f"🔍 在新資料庫找到對應技令: {corresponding_id}")
                # 收集新資料庫的檔案ID
                all_file_ids.update(corresponding_result.get("image_id_list", []))
                all_file_ids.update(corresponding_result.get("video_id_list", []))
                all_file_ids.update(corresponding_result.get("pdf_id_list", []))
            
        elif new_result and not old_result:
            # 新資料庫有，舊資料庫沒有 → 用新資料庫的 subClass + optionClass 去舊資料庫找
            new_sub_class = new_result.get("subClass", "")
            new_option_class = new_result.get("optionClass", "")
            
            # 組合成舊資料庫的格式
            if new_option_class and new_sub_class:
                search_combined_class = f"{new_sub_class} - {new_option_class}"
            else:
                search_combined_class = new_sub_class
            
            # 在舊資料庫中搜尋匹配的技令
            corresponding_result = self.get_order_collection().find_one({
                "stepName": primary_result["stepName"],
                "stepNumber": primary_result["stepNumber"],
                "mainClass": primary_result["mainClass"],
                "subClass": search_combined_class
            })
            
            if corresponding_result:
                corresponding_id = corresponding_result["_id"]
                print(f"🔍 在舊資料庫找到對應技令: {corresponding_id}")
                # 收集舊資料庫的檔案ID
                all_file_ids.update(corresponding_result.get("image_id_list", []))
                all_file_ids.update(corresponding_result.get("video_id_list", []))
                all_file_ids.update(corresponding_result.get("pdf_id_list", []))

        print(f"📁 總共需要刪除 {len(all_file_ids)} 個檔案")

        try:
            # 🔧 決定使用哪個 session
            if external_session is not None:
                chosen_session = external_session
            else:
                chosen_session = None

            def execute_deletion(session):
                # 刪除檔案
                for file_id in all_file_ids:
                    self.delete_order_file(file_id, session=session)
                    print(f"🗑️ 標記刪除檔案: {file_id}")

                # 刪除主要目標
                if old_result:
                    delete_result_old = self.get_order_collection().delete_one(
                        {"_id": ObjectId(technical_order_id)}, session=session
                    )
                    print(f"🗂️ 舊資料庫刪除結果: {delete_result_old.deleted_count} 筆")

                if new_result:
                    delete_result_new = self.get_new_order_collection().delete_one(
                        {"_id": ObjectId(technical_order_id)}, session=session
                    )
                    print(f"🗂️ 新資料庫刪除結果: {delete_result_new.deleted_count} 筆")
                
                # 刪除對應的技令
                if corresponding_result and corresponding_id:
                    if old_result and not new_result:
                        # 刪除新資料庫的對應技令
                        delete_result_corresponding = self.get_new_order_collection().delete_one(
                            {"_id": corresponding_id}, session=session
                        )
                        print(f"🗂️ 新資料庫對應技令刪除結果: {delete_result_corresponding.deleted_count} 筆")
                    elif new_result and not old_result:
                        # 刪除舊資料庫的對應技令
                        delete_result_corresponding = self.get_order_collection().delete_one(
                            {"_id": corresponding_id}, session=session
                        )
                        print(f"🗂️ 舊資料庫對應技令刪除結果: {delete_result_corresponding.deleted_count} 筆")

            # 🔧 執行刪除操作
            if chosen_session is not None:
                # 使用外部 session
                execute_deletion(chosen_session)
            else:
                # 使用內部 session
                with mongo_client.start_session() as session:
                    with session.start_transaction():
                        execute_deletion(session)
            
            print(f"✅ 技令刪除完成，ID: {technical_order_id}")

        except Exception as e:
            print(f"❌ 刪除技令時發生錯誤: {str(e)}")
            traceback.print_exc()
            raise Exception(f"Technical Order Deletion Failed: {str(e)}")

    # patch
    def update_technical_order(
        self, technical_order_id: str, image_list, video_list, request_data
    ):
        # get image_id_list, video_id_list
        result = self.get_order_collection().find_one(
            {"_id": ObjectId(technical_order_id)}
        )
        print(result)

        for key, value in request_data.items():
            result[key] = value

        result = self._add_sort_columns(result)

        # update data except image_list, video_list
        self.get_order_collection().update_one(
            {"_id": ObjectId(technical_order_id)}, {"$set": result}
        )

    def update_technical_order_images(self, technical_order_id: str, image_list):
        # get image_id_list
        result = self.get_order_collection().find_one(
            {"_id": ObjectId(technical_order_id)}
        )
        print(result)
        new_image_id_list = []
        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # remove image_list in local storage and database
                    for image_id in result["image_id_list"]:
                        self.delete_order_file(image_id, session=session)

                    self.get_order_collection().update_one(
                        {"_id": ObjectId(technical_order_id)},
                        {"$set": {"image_id_list": []}},
                        session=session,
                    )

                    # save image_list in database
                    image_id_list = []

                    if image_list[0] == "null":
                        return

                    for image in image_list:
                        image_data = {
                            "file_name": image.filename,
                            "type": "image",
                            "extension": image.filename.split(".")[-1],
                        }
                        id = ObjectId()
                        image_data["_id"] = id
                        id = str(id)
                        self.get_order_upload_file_collection().insert_one(
                            image_data, session=session
                        )

                        new_image_id_list.append(id)

                        # save image_list, video_list in local storage
                        with open(
                            f"./storage/{id}.{image_data['extension']}", "wb"
                        ) as f:
                            f.write(image.file.read())

                        image_id_list.append(id)

                    result["image_id_list"] = image_id_list

                    self.get_order_collection().update_one(
                        {"_id": ObjectId(technical_order_id)},
                        {"$set": result},
                        session=session,
                    )
        except:
            # remove image_list in local storage
            for f in os.listdir("./storage"):
                if f.split(".")[0] in new_image_id_list:
                    os.remove(f"./storage/{f}")
            traceback.print_exc()
            raise Exception("Technical Order Image Update Failed")

    def update_technical_order_videos(self, technical_order_id: str, video_list):
        try:
            new_video_id_list = []
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # get video_id_list
                    result = self.get_order_collection().find_one(
                        {"_id": ObjectId(technical_order_id)}
                    )
                    print(result)

                    # remove video_list in local storage and database
                    for video_id in result["video_id_list"]:
                        self.delete_order_file(video_id, session=session)

                    self.get_order_collection().update_one(
                        {"_id": ObjectId(technical_order_id)},
                        {"$set": {"video_id_list": []}},
                        session=session,
                    )

                    # save video_list in database
                    video_id_list = []

                    if video_list[0] == "null":
                        return

                    for video in video_list:
                        video_data = {
                            "file_name": video.filename,
                            "type": "video",
                            "extension": video.filename.split(".")[-1],
                        }
                        id = ObjectId()
                        video_data["_id"] = id
                        id = str(id)
                        self.get_order_upload_file_collection().insert_one(
                            video_data, session=session
                        )

                        new_video_id_list.append(id)
                        # save image_list, video_list in local storage
                        with open(
                            f"./storage/{id}.{video_data['extension']}", "wb"
                        ) as f:
                            f.write(video.file.read())

                        video_id_list.append(id)

                    result["video_id_list"] = video_id_list

                    self.get_order_collection().update_one(
                        {"_id": ObjectId(technical_order_id)},
                        {"$set": result},
                        session=session,
                    )
        except:
            # remove  video_list in local storage
            for f in os.listdir("./storage"):
                if f.split(".")[0] in new_video_id_list:
                    os.remove(f"./storage/{f}")
            raise Exception("Technical Order Video Update Failed")

    def update_technical_order_pdfs(self, technical_order_id: str, pdf_list):
        try:
            new_pdf_id_list = []
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # get pdf_id_list
                    result = self.get_order_collection().find_one(
                        {"_id": ObjectId(technical_order_id)}
                    )
                    print(result)

                    # remove pdf_list in local storage and database
                    for pdf_id in result["pdf_id_list"]:
                        self.delete_order_file(pdf_id, session=session)

                    self.get_order_collection().update_one(
                        {"_id": ObjectId(technical_order_id)},
                        {"$set": {"pdf_id_list": []}},
                        session=session,
                    )

                    # save pdf_list in database
                    pdf_id_list = []

                    if pdf_list[0] == "null":
                        return

                    for pdf in pdf_list:
                        pdf_data = {
                            "file_name": pdf.filename,
                            "type": "pdf",
                            "extension": pdf.filename.split(".")[-1],
                        }
                        id = ObjectId()
                        pdf_data["_id"] = id
                        id = str(id)
                        self.get_order_upload_file_collection().insert_one(
                            pdf_data, session=session
                        )

                        new_pdf_id_list.append(id)
                        # save image_list, video_list in local storage
                        with open(f"./storage/{id}.{pdf_data['extension']}", "wb") as f:
                            f.write(pdf.file.read())

                        pdf_id_list.append(id)

                    result["pdf_id_list"] = pdf_id_list

                    self.get_order_collection().update_one(
                        {"_id": ObjectId(technical_order_id)},
                        {"$set": result},
                        session=session,
                    )
        except:
            # remove pdf_list in local storage
            for f in os.listdir("./storage"):
                if f.split(".")[0] in new_pdf_id_list:
                    os.remove(f"./storage/{f}")
            raise Exception("Technical Order PDF Update Failed")

    def is_file_size_under_limit(self, all_file_list: List[List[UploadFile]]):
        for file_list in all_file_list:
            for file in file_list:
                if file.file.seek(0, os.SEEK_END) > self.FILE_SIZE_LIMIT:
                    return False
        return True


##########################   嘗試撰寫新的技令後端API 2025/02/26 ########################## 
    def get_new_technical_order(
        self,
        technical_order_id=None,
        main_class=None,
        sub_class=None,
        option_class=None,
        original_id=None,
        page_mode=None,
        last_id=None,
    ):
        if sub_class == "全部":
            sub_class = None
        if option_class == "全部":
            option_class = None
        if main_class == "all" or main_class == "全部":
            main_class = None

        if original_id == "all" or original_id == "全部":
            original_id = None

        # 確保 main_class 不會被 original_id 覆蓋
        if original_id:
            main_class = original_id  # 只在 original_id 存在時才改變 main_class
        print(" main_class:", main_class, " sub_class:", sub_class, " option_class:", option_class, "page mode:",page_mode)
        print()
        if technical_order_id is not None:
            return self.get_new_order_collection().find_one(
                {"_id": ObjectId(technical_order_id)}
            )

        elif sub_class is not None and main_class is not None and option_class is not None:
            if page_mode is not None:
                if last_id is None:
                    # print("main_class : ", main_class, "sub_class : ", sub_class, "option_class", option_class)
                    return (
                        self.get_new_order_collection()
                        .find({"mainClass": main_class, "subClass": sub_class, "optionClass" : option_class})
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
                if last_id is not None:
                    # get sort column info of last_id
                    last_order = self.get_new_order_collection().find_one(
                        {"_id": ObjectId(last_id)}
                    )
                    return (
                        self.get_new_order_collection()
                        .find(
                            {
                                "mainClass": main_class,
                                "subClass": sub_class,
                                "optionClass" : option_class,
                                "$or": [
                                    {
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": last_order[
                                            "sort_step_number"
                                        ],
                                        "_id": {"$gt": ObjectId(last_id)},
                                    },
                                    {
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": {
                                            "$gt": last_order["sort_step_number"]
                                        },
                                    },
                                    {"sort_tags": {"$gt": last_order["sort_tags"]}},
                                ],
                            }
                        )
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
            return self.get_new_order_collection().find(
                {"mainClass": main_class, "subClass": sub_class, "optionClass" : option_class}
            )

        elif main_class is not None and sub_class is not None:
            if page_mode is not None:
                if last_id is None:
                    return (
                        self.get_new_order_collection()
                        .find({"mainClass": main_class, "subClass" : sub_class})
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
                if last_id is not None:
                    last_order = self.get_new_order_collection().find_one(
                        {"_id": ObjectId(last_id)}
                    )
                    return (
                        self.get_new_order_collection()
                        .find(
                            {
                                "mainClass": main_class,
                                'subClass' : sub_class,
                                "$or": [
                                    {
                                        "optionClass": last_order["optionClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": last_order[
                                            "sort_step_number"
                                        ],
                                        "_id": {"$gt": ObjectId(last_id)},
                                    },
                                    {
                                        "optionClass": last_order["optionClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": {
                                            "$gt": last_order["sort_step_number"]
                                        },
                                    },
                                    {
                                        "optionClass": last_order["optionClass"],
                                        "sort_tags": {"$gt": last_order["sort_tags"]},
                                    },
                                    {
                                        "optionClass": {"$gt": last_order["optionClass"]},
                                    },
                                ],
                            }
                        )
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
            return self.get_new_order_collection().find({"mainClass": main_class, "subClass" : sub_class})
        # 如果 main_class 不為null
        elif main_class is not None:
            print("修改中...")
            if page_mode is not None:
                if last_id is None:
                    return (
                        self.get_new_order_collection()
                        .find({"mainClass": main_class})
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
                if last_id is not None:
                    last_order = self.get_new_order_collection().find_one(
                        {"_id": ObjectId(last_id)}
                    )
                    return (
                        self.get_new_order_collection()
                        .find(
                            {
                                "mainClass": main_class,
                                "$or": [
                                    {
                                        "subClass": last_order["subClass"],
                                        "optionClass": last_order["optionClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": last_order[
                                            "sort_step_number"
                                        ],
                                        "_id": {"$gt": ObjectId(last_id)},
                                    },
                                    {
                                        "subClass": last_order["subClass"],
                                        "optionClass": last_order["optionClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": {
                                            "$gt": last_order["sort_step_number"]
                                        },
                                    },
                                    {
                                        "subClass": last_order["subClass"],
                                        "optionClass": last_order["optionClass"],
                                        "sort_tags": {"$gt": last_order["sort_tags"]},
                                    },
                                    {
                                        "subClass": last_order["subClass"],
                                        "optionClass": last_order["optionClass"],
                                    },
                                    {"subClass": last_order["subClass"],},
                                ]
                            }
                        )
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
            return self.get_order_collection().find({"mainClass": main_class})
        
        else:
            if page_mode is not None:
                if last_id is None:
                    return (
                        self.get_new_order_collection()
                        .find({})
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
                if last_id is not None:
                    last_order = self.get_new_order_collection().find_one(
                        {"_id": ObjectId(last_id)}
                    )
                    return (
                        self.get_new_order_collection()
                        .find(
                            {
                                "$or": [
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": last_order["subClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": last_order[
                                            "sort_step_number"
                                        ],
                                        "_id": {"$gt": ObjectId(last_id)},
                                    },
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": last_order["subClass"],
                                        "sort_tags": last_order["sort_tags"],
                                        "sort_step_number": {
                                            "$gt": last_order["sort_step_number"]
                                        },
                                    },
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": last_order["subClass"],
                                        "sort_tags": {"$gt": last_order["sort_tags"]},
                                    },
                                    {
                                        "mainClass": last_order["mainClass"],
                                        "subClass": {"$gt": last_order["subClass"]},
                                    },
                                    {"mainClass": {"$gt": last_order["mainClass"]}},
                                ]
                            }
                        )
                        .sort(self.SORT_COLUMN)
                        .limit(self.PAGE_LIMIT)
                    )
            return self.get_new_order_collection().find({})