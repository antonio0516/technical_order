import datetime
from enum import Enum

from domain.database.database import mongo_client, mongo_database


class LogType(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AdminLog:
    def __init__(self):
        self.MAX_LOG = 1500

    def get_collection(self):
        return mongo_database.admin_log

    def get_all_log(self):
        return self.get_collection().find().sort([("created_at", -1)])

    def add_log(self, message, user_info, tag, type: LogType, datetime_info=None):
        try:
            with mongo_client.start_session() as session:
                with session.start_transaction():
                    if datetime_info is None:
                        datetime_info = datetime.datetime.now()

                    log = {
                        "message": message,
                        "account": user_info["account"],
                        "created_at": datetime_info.strftime("%Y-%m-%d %H:%M:%S"),
                        "tag": tag,
                        "type": type.value,
                    }
                    self.get_collection().insert_one(log, session=session)

                    # check if the log is over the limit
                    log_count = self.get_collection().count_documents({})
                    if log_count >= self.MAX_LOG:
                        self._remove_oldest_log(session=session)
        except Exception as e:
            raise Exception("Add log failed")

    def _remove_oldest_log(self, session=None):
        # remove until the log count is less than the limit
        log_count = self.get_collection().count_documents({})

        oldest_log = (
            self.get_collection()
            .find()
            .sort([("created_at", 1)])
            .limit(log_count - self.MAX_LOG + 1)
        )
        self.get_collection().delete_many(
            {
                "_id": {"$in": [log["_id"] for log in oldest_log]},
            },
            session=session,
        )

    def clear_log(self):
        self.get_collection().delete_many({})
