from secrets import token_hex, token_urlsafe

from bson import ObjectId

from domain.database.database import mongo_database


class Student:
    HELICOPTER_TYPES = ["AH-1W", "OH-58D"]

    def get_student_collection(self):
        return mongo_database.student

    def get_students(self):
        return self.get_student_collection().find()

    def get_student_by_student_number(self, student_number):
        return self.get_student_collection().find_one(
            {"student_number": student_number}
        )

    def get_id_by_student_number(self, student_number):
        return self.get_student_collection().find_one(
            {"student_number": student_number}
        )["_id"]

    def get_student_by_id(self, id):
        return self.get_student_collection().find_one({"_id": ObjectId(id)})

    def delete_all_students(self, session=None):
        return self.get_student_collection().delete_many({}, session=session)

    def delete_student_by_id(self, id, session=None):
        return self.get_student_collection().delete_one(
            {"_id": ObjectId(id)}, session=session
        )

    def create_student_info(self, student_number):
        student_data = {
            "student_number": str(student_number),
            "exam_token": token_urlsafe(16),
            "exam_flag": {
                helicopter_type: False for helicopter_type in self.HELICOPTER_TYPES
            },
            "grade": {helicopter_type: -1 for helicopter_type in self.HELICOPTER_TYPES},
            "password": token_hex(5),
        }

        return student_data

    def create_students_by_continuous_number(self, start, end, session=None):
        for i in range(start, end + 1):
            self.get_student_collection().insert_one(
                self.create_student_info(student_number=i), session=session
            )

    def create_student(self, student_number, session=None):
        self.get_student_collection().insert_one(
            self.create_student_info(student_number), session=session
        )

    def update_student_grade(self, student_number, grade, type):
        origin_grade = self.get_student_by_student_number(student_number)["grade"]
        origin_grade[type] = grade
        self.get_student_collection().update_one(
            {"student_number": str(student_number)}, {"$set": {"grade": origin_grade}}
        )

    def update_student_exam_flag(self, id, type, flag):
        exam_flag = self.get_student_by_id(id)["exam_flag"]
        exam_flag[type] = flag
        self.get_student_collection().update_one(
            {"_id": ObjectId(id)}, {"$set": {"exam_flag": exam_flag}}
        )
