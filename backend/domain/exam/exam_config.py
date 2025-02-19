from enum import Enum
from secrets import token_hex, token_urlsafe

from bson import ObjectId

from domain.database.database import mongo_database


class ExamConfigColumn(Enum):
    EXAM_TIME = "exam_time"


class ExamConfig:
    DEFAULT_EXAM_CONFIG = {
        "exam_time": 60,  # seconds
    }

    def get_exam_config_collection(self):
        return mongo_database.exam_config

    def set_exam_config_column(self, exam_column: ExamConfigColumn, value):
        exam_column = exam_column.value

        # check if exam_column exists
        exam_config = self.get_exam_config_collection().find_one({"name": exam_column})
        if exam_config:
            self.get_exam_config_collection().update_one(
                {"name": exam_column}, {"$set": {"value": value}}
            )
        else:
            self.get_exam_config_collection().insert_one(
                {"name": exam_column, "value": value}
            )

    def get_exam_config_column(self, exam_column: ExamConfigColumn):
        exam_column = exam_column.value
        # check if exam_column exists
        exam_config = self.get_exam_config_collection().find_one({"name": exam_column})
        print(exam_config)
        if exam_config:
            return exam_config["value"]

        # check if exam_column exists in DEFAULT_EXAM_CONFIG
        if exam_column in self.DEFAULT_EXAM_CONFIG:
            self.get_exam_config_collection().insert_one(
                {"name": exam_column, "value": self.DEFAULT_EXAM_CONFIG[exam_column]}
            )
            return self.DEFAULT_EXAM_CONFIG[exam_column]
        else:
            return None
