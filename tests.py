
import unittest
import tempfile
import os
import json

from models import BaseProduct, Clothing, Furniture
from validation import ValidationError
from utils import parse_json, set_write_off_date

#Тестирование базового класса
class TestBaseProduct(unittest.TestCase):
    def test_base_product_valid(self):
        """Проверяем корректное создание базового продукта с валидными данными"""
        data = {"name": "Product A", "date_of_receipt": "10.04.2025", "count": 5}
        product = BaseProduct(data)
        self.assertEqual(product.name, "Product A")
        self.assertEqual(product.count, 5)
        self.assertEqual(product.formated_date_of_receipt, "10.04.2025")
        self.assertEqual(product.formated_date_of_write_off, "Не списано")

    def test_base_product_missing_field(self):
        """Проверяем, что при отсутствии обязательного поля выбрасывается исключение"""
        data = {"name": "Product A", "date_of_receipt": "10.04.2025"}
        with self.assertRaises(ValidationError):
            BaseProduct(data)

    def test_base_product_invalid_date(self):
        """Проверяем, что неверный формат даты вызывает ошибку валидации"""
        data = {"name": "Product A", "date_of_receipt": "2025-04-10", "count": 5}
        with self.assertRaises(ValidationError):
            BaseProduct(data)

#Тестирование класса одежды
class TestClothing(unittest.TestCase):
    def test_clothing_valid(self):
        """Проверяем создание объекта Clothing с правильными данными"""
        data = {
            "name": "Shirt",
            "date_of_receipt": "10.04.2025",
            "count": 10,
            "size": "M",
            "color": "Red",
            "material": "Cotton"
        }
        product = Clothing(data)
        self.assertEqual(product.size, "M")
        self.assertEqual(product.color, "Red")
        self.assertEqual(product.material, "Cotton")

    def test_clothing_invalid_size(self):
        """Проверяем, что неверное значение размера (не из списка допустимых) вызывает исключение"""
        data = {
            "name": "Shirt",
            "date_of_receipt": "10.04.2025",
            "count": 10,
            "size": "XX",
            "color": "Red",
            "material": "Cotton"
        }
        with self.assertRaises(ValidationError):
            Clothing(data)

#Тестирование класса мебели
class TestFurniture(unittest.TestCase):
    def test_furniture_valid(self):
        """Проверяем создание объекта Furniture с валидными данными"""
        data = {
            "name": "Table",
            "date_of_receipt": "10.04.2025",
            "count": 3,
            "material": "Wood",
            "dimensions": "100x50x30",
            "weight": 20
        }
        product = Furniture(data)
        self.assertEqual(product.dimensions, "100x50x30")
        self.assertEqual(product.weight, 20)

    def test_furniture_invalid_dimensions(self):
        """Проверяем, что неверный формат размеров вызывает исключение"""
        data = {
            "name": "Table",
            "date_of_receipt": "10.04.2025",
            "count": 3,
            "material": "Wood",
            "dimensions": "100x50",
            "weight": 20
        }
        with self.assertRaises(ValidationError):
            Furniture(data)

#Тестирование Utils
class TestUtils(unittest.TestCase):
    def test_set_write_off_date_valid(self):
        """Проверяем установку корректной даты списания"""
        data = {"name": "Product A", "date_of_receipt": "10.04.2025", "count": 5}
        product = BaseProduct(data)
        set_write_off_date(product, "15.04.2025")
        self.assertEqual(product.formated_date_of_write_off, "15.04.2025")

    def test_set_write_off_date_invalid(self):
        """Проверяем, что установка некорректной даты списания вызывает ошибку валидации"""
        data = {"name": "Product A", "date_of_receipt": "10.04.2025", "count": 5}
        product = BaseProduct(data)
        with self.assertRaises(ValidationError):
            set_write_off_date(product, "invalid_date")

    def test_parse_json_valid(self):
        """
        Тестируем функцию parse_json:
        создаем временный JSON-файл с одним продуктом и проверяем,
        что функция возвращает корректный список объектов.
        """
        test_data = {
            "Prod1": {
                "name": "Product A",
                "date_of_receipt": "10.04.2025",
                "count": 5
            }
        }
        tmp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json')
        json.dump(test_data, tmp_file, indent=2)
        tmp_file.close()
        try:
            products = parse_json(tmp_file.name)
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0].name, "Product A")
        finally:
            os.unlink(tmp_file.name)

if __name__ == '__main__':
    unittest.main()
