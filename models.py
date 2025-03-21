from datetime import datetime
from validation import ValidationError

class BaseProduct:
    def __init__(self, data: dict):
        required_fields = ["name", "date_of_receipt", "count"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Field '{field}' is missing")

        self.name = data["name"]

        try:
            self.date_of_receipt = datetime.strptime(data["date_of_receipt"], "%d.%m.%Y")
        except ValueError:
            raise ValidationError("Не верный формат даты, ожидается 'DD.MM.YYYY'")

        if "date_of_write_off" in data:
            try:
                self.date_of_write_off = datetime.strptime(data["date_of_write_off"], "%d.%m.%Y")
            except ValueError:
                raise ValidationError("Неверный формат даты списания, ожидается 'DD.MM.YYYY'")
        else:
            self.date_of_write_off = None

        if not isinstance(data["count"], int):
            raise ValidationError("Поле 'count' должно быть числом")
        self.count = data["count"]

    @property
    def formated_date_of_receipt(self):
        return self.date_of_receipt.strftime('%d.%m.%Y')

    @property
    def formated_date_of_write_off(self):
        if self.date_of_write_off:
            return self.date_of_write_off.strftime('%d.%m.%Y')
        return "Не списано"


class Clothing(BaseProduct):
    def __init__(self, data: dict):
        super().__init__(data)

        required_fields = ["size", "color", "material"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Поле '{field}' отсутствует в Clothing")

        sizes = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

        if data["size"] not in sizes:
            raise ValidationError(f"Поле 'size' неверно задано")

        self.size = data["size"]
        self.color = data["color"]
        self.material = data["material"]

    def __repr__(self):
        return (f"<Clothing name={self.name}, date={self.formated_date_of_receipt}, "
                f"count={self.count}, size={self.size}, color={self.color}>, material={self.material}, write_off_date={self.formated_date_of_write_off}")


class Furniture(BaseProduct):
    def __init__(self, data: dict):
        super().__init__(data)

        required_fields = ["material", "dimensions", "weight"]

        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Field '{field}' is missing in Furniture")

        self.material = data["material"]

        dimensions_str = data["dimensions"]
        dimensions_parts = dimensions_str.split('x')
        if len(dimensions_parts) != 3:
            raise ValidationError("Размеры должны быть в формате <int>x<int>x<int>")
        try:
            width = int(dimensions_parts[0])
            length = int(dimensions_parts[1])
            height = int(dimensions_parts[2])
        except:
            raise ValidationError("Размеры должны быть только числами")
        if width <= 0 or length <= 0 or height <= 0:
            raise ValidationError("Размеры должны быть положительными числами")

        self.dimensions = data["dimensions"]

        if not isinstance(data["weight"], int):
            raise ValidationError("Поле 'weight' должно быть числом")
        if data["weight"] < 0:
            raise ValidationError("Поле 'weight' должно быть положительным")

        self.weight = data["weight"]

    def __repr__(self):
        return (f"<Furniture name={self.name}, date={self.formated_date_of_receipt}, "
                f"count={self.count}, material={self.material}, dimensions={self.dimensions}, weight={self.weight}, write_off_date={self.formated_date_of_write_off}>")
