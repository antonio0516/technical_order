import re

from domain.database.database import mongo_client, mongo_database

technical_order_collection = mongo_database.technical_order


def extract_and_format_numbers(input_str):
    numbers = re.findall(r"\d+", input_str)
    formatted_numbers = [f"{int(num):04}" for num in numbers]
    result = ".".join(formatted_numbers)
    return result


with mongo_client.start_session() as session:
    with session.start_transaction():
        for item in technical_order_collection.find():
            tags = item["tags"]
            sort_tags = sorted(tags)
            sort_tags = ",".join(sort_tags)
            item["sort_tags"] = sort_tags
            technical_order_collection.update_one(
                {"_id": item["_id"]},
                {"$set": {"sort_tags": sort_tags}},
                session=session,
            )

        for item in technical_order_collection.find():
            step_number = item["stepNumber"]

            if step_number == "":
                item["sort_step_number"] = ""
            else:
                formatted_step_number = extract_and_format_numbers(step_number)
                item["sort_step_number"] = formatted_step_number
            technical_order_collection.update_one(
                {"_id": item["_id"]},
                {"$set": {"sort_step_number": formatted_step_number}},
                session=session,
            )
