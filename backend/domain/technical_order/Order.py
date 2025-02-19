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
        ("sort_tags", 1),
        ("sort_step_number", 1),
        ("_id", 1),
    ]

    def __init__(self):
        pass

    def get_order_collection(self):
        return mongo_database.technical_order

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
        request_data,
    ):
        """
        TODO: validate technical_order format
        """
        image_id_list = []
        video_id_list = []
        pdf_id_list = []

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # save image_list, video_list in database
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

                    request_data["image_id_list"] = image_id_list
                    request_data["video_id_list"] = video_id_list
                    request_data["pdf_id_list"] = pdf_id_list

                    request_data = self._add_sort_columns(request_data)

                    self.get_order_collection().insert_one(
                        request_data, session=session
                    )
        except:
            # remove image_list, video_list in local storage
            merge_list = image_id_list + video_id_list + pdf_id_list
            for f in os.listdir("./storage"):
                if f.split(".")[0] in merge_list:
                    os.remove(f"./storage/{f}")
            traceback.print_exc()
            raise Exception("Technical Order Insertion Failed")

    def duplicate_technical_order(self, technical_order_id: str):
        new_file_id_list = []
        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    # get technical_order
                    result = self.get_order_collection().find_one(
                        {"_id": ObjectId(technical_order_id)}
                    )

                    original_result = deepcopy(result)

                    # duplicate technical_order
                    result.pop("_id")

                    file_columns = ["image_id_list", "video_id_list", "pdf_id_list"]

                    # remove file
                    for column in file_columns:
                        result[column] = []

                    new_id = ObjectId()
                    result["_id"] = new_id
                    self.get_order_collection().insert_one(result, session=session)

                    # duplicate file
                    for file_column in file_columns:
                        for file_id in original_result[file_column]:
                            file = self.get_upload_file(file_id)
                            file.pop("_id")
                            new_file_id = ObjectId()
                            file["_id"] = new_file_id
                            self.get_order_upload_file_collection().insert_one(file)

                            # duplicate file in file management
                            new_file_id_list.append(str(new_file_id))
                            shutil.copy(
                                f"./storage/{file_id}.{file['extension']}",
                                f"./storage/{new_file_id}.{file['extension']}",
                            )

                            self.get_order_collection().update_one(
                                {"_id": new_id},
                                {"$push": {file_column: str(new_file_id)}},
                                session=session,
                            )
        except:
            # remove image_list, video_list in local storage
            for f in os.listdir("./storage"):
                if f.split(".")[0] in new_file_id_list:
                    os.remove(f"./storage/{f}")
            raise Exception("Technical Order Duplication Failed")

    def get_technical_order(
        self,
        technical_order_id=None,
        main_class=None,
        sub_class=None,
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
        # get image_id_list, video_id_list
        result = self.get_order_collection().find_one(
            {"_id": ObjectId(technical_order_id)}
        )

        print(result)

        image_id_list = result["image_id_list"]
        video_id_list = result["video_id_list"]
        pdf_id_list = result["pdf_id_list"]

        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    chosen_session = (
                        session if external_session is None else external_session
                    )
                    # remove image_list, video_list in local storage and database
                    for image_id in image_id_list:
                        self.delete_order_file(image_id, session=chosen_session)
                    for video_id in video_id_list:
                        self.delete_order_file(video_id, session=chosen_session)
                    for pdf_id in pdf_id_list:
                        self.delete_order_file(pdf_id, session=chosen_session)

                    # remove technical_order in database
                    self.get_order_collection().delete_one(
                        {"_id": ObjectId(technical_order_id)}, session=chosen_session
                    )
        except:
            raise Exception("Technical Order Deletion Failed")

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
