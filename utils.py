# utils.py
import json
import logging
from models import BaseProduct, Clothing, Furniture
from validation import ValidationError


logger = logging.getLogger("ProductParser")
logger.setLevel(logging.INFO)
if not logger.handlers:
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def parse_json(filename):
    """
    Читает JSON-файл с продуктами и пытается создать объекты продуктов.
    Если данные для отдельного продукта некорректны, ошибка регистрируется в лог,
    а продукт пропускается.
    """
    products = []
    try:
        with open(filename, 'r', encoding="UTF-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Ошибка открытия или чтения файла {filename}: {e}")
        return products

    for key, item in data.items():
        try:
            if "size" in item and "color" in item and "material" in item:
                product = Clothing(item)
            elif "dimensions" in item and "weight" in item and "material" in item:
                product = Furniture(item)
            else:
                product = BaseProduct(item)
            products.append(product)
        except ValidationError as ve:
            logger.error(f"Ошибка обработки продукта {key}: {ve}")
            continue
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при обработке продукта {key}: {e}")
            continue
    return products

def set_write_off_date(product, date_str):
    """
    Устанавливает дату списания для переданного продукта.
    Функция проверяет корректность формата даты, и в случае ошибки поднимает ValidationError.
    """
    from datetime import datetime
    try:
        new_date = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError as ve:
        raise ValidationError("Неверный формат даты списания, ожидается 'DD.MM.YYYY'") from ve

    if new_date < product.date_of_receipt:
        raise ValidationError("Дата списания не может быть раньше даты поступления")

    product.date_of_write_off = new_date

if __name__ == "__main__":
    products = parse_json("example.json")
    for prod in products:
        print(prod)
