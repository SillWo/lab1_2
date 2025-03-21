import json
from models import BaseProduct, Clothing, Furniture
from validation import ValidationError
from datetime import datetime

def set_write_off_date(product: BaseProduct, write_off_date: str):
    try:
        product.date_of_write_off = datetime.strptime(write_off_date, "%d.%m.%Y")
    except ValueError:
        raise ValidationError("Неверный формат даты, ожидается 'DD.MM.YYYY'")

def parse_json(filename: str):
    objects_list = []

    with open(filename, 'r', encoding="UTF-8") as f:
        data = json.loads(f.read())

    for key, value in data.items():
        try:
            obj = Furniture(value)
            objects_list.append(obj)
        except ValidationError:
            try:
                obj = Clothing(value)
                objects_list.append(obj)
            except ValidationError:
                try:
                    obj = BaseProduct(value)
                    objects_list.append(obj)
                except ValidationError as e:
                    print(f"Ошибка с {key}: {e}")

    return objects_list
