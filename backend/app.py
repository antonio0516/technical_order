import argparse
import signal
from multiprocessing import Process

import psutil

from domain.get_config import Config, ConfigMode

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # dev flog
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    if args.dev:
        Config.set_mode(ConfigMode.DEV)
        print("devlopment mode")
    else:
        Config.set_mode(ConfigMode.PROD)
        print("production mode")


import os
import sys
import threading
import time
import traceback
from contextlib import asynccontextmanager

import psutil
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller import admin_logs, auth, exam_config, students, users
from controller.technical_orders import (main_classes, order_template_columns,
                                         orders, tags, versions, option_classes) #join option_classes
from domain.admin_log import AdminLog
from domain.database.database import mongo_client, mongo_database
from domain.technical_order.Order import Order
from domain.technical_order.OrderTemplate import OrderTemplate
from domain.technical_order.Version import Version


def shutdown():
    parent_pid = os.getpid()
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()


def init():
    order_template = OrderTemplate()
    technical_order_collection = mongo_database.technical_order
    # check if order_template_column is empty
    # if empty, add default order_template_column
    if order_template.get_all_order_template_column() == []:
        order_template.reset_default_order_template_column()

    # create index
    with mongo_client.start_session() as session:
        with session.start_transaction():
            technical_order_collection.create_index(
                [
                    ("mainClass", 1),
                    ("subClass", 1),
                    ("sort_tags", 1),
                    ("sort_step_number", 1),
                    ("_id", 1),
                ],
                name="mainClass_subClass_sort_tags_sort_step_number_id",
            )


def end_button_func():
    # signal.SIGINT # if you are using ubuntu or mac
    # signal.CTRL_C_EVENT # if you are using windows
    # check os if windows or linux
    if sys.platform == "win32":
        os.kill(os.getpid(), signal.CTRL_C_EVENT)
    else:
        os.kill(os.getpid(), signal.SIGINT)


def delete_file_routine():
    while True:
        # delete deleted upload file
        order = Order()
        deleted_file_list = order.get_order_upload_file_collection().find(
            {"delete_flag": True}
        )
        version = Version()
        deleted_version_list = version.get_version_collection().find(
            {"deleted_flag": True}
        )

        for item in deleted_file_list:
            try:
                order.remove_order_file_completely(str(item["_id"]))
                # raise Exception("test")
                print(f"delete file: {item['_id']}")
            except:
                print(f"delete file failed: {item['_id']}")
                threading.Timer(1, end_button_func).start()
                threading.Timer(6, shutdown).start()
                traceback.print_exc()
                continue

        for item in deleted_version_list:
            try:
                version.remove_version_completely(str(item["_id"]))
                print(f"delete version: {item['_id']}")
            except:
                print(f"delete version failed: {item['_id']}")
                threading.Timer(1, end_button_func).start()
                threading.Timer(6, shutdown).start()
                traceback.print_exc()
                continue


@asynccontextmanager
async def lifespan(app: FastAPI):
    delete_file_routine_thread = threading.Thread(
        target=delete_file_routine,
    )
    delete_file_routine_thread.daemon = True
    delete_file_routine_thread.start()

    yield


admin_log = AdminLog()

app = FastAPI(lifespan=lifespan)
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(students.router, prefix="/students")
api_router.include_router(admin_logs.router, prefix="/admin_logs")
api_router.include_router(exam_config.router, prefix="/exam_config")
api_router.include_router(main_classes.router, prefix="/technical_orders/main_classes")
api_router.include_router(tags.router, prefix="/technical_orders/tags")
api_router.include_router(
    order_template_columns.router, prefix="/technical_orders/order_template_columns"
)
api_router.include_router(orders.router, prefix="/technical_orders/orders")
api_router.include_router(versions.router, prefix="/technical_orders/versions")
api_router.include_router(option_classes.router, prefix="/technical_orders/option_classes")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api_router.get("/")
def hello_world():
    return {"status": "health"}


app.include_router(api_router)

if __name__ == "__main__":
    init()

    uvicorn.run(app="app:app", host="0.0.0.0", port=8000, reload=False, workers=1)
