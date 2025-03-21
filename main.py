import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class UI:
    def __init__(self, master, filename):
        self.master = master
        self.filename = filename
        self.products = []

        master.title("Менеджмент склада")
        master.geometry("1200x600")

        # Создаем панель инструментов
        self.toolbar = ttk.Frame(master)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Кнопки управления
        self.add_btn = ttk.Button(self.toolbar, text="Добавить продукт", command=self.add_product)
        self.add_btn.pack(side=tk.LEFT, padx=2)

        self.write_off_btn = ttk.Button(self.toolbar, text="Списать выбранное", command=self.write_off_product)
        self.write_off_btn.pack(side=tk.LEFT, padx=2)

        self.remove_btn = ttk.Button(self.toolbar, text="Удалить выбранное", command=self.remove_product)
        self.remove_btn.pack(side=tk.LEFT, padx=2)

        self.save_btn = ttk.Button(self.toolbar, text="Сохранить", command=self.save_data)
        self.save_btn.pack(side=tk.RIGHT, padx=2)

        # Создаем таблицу
        self.tree = ttk.Treeview(master, columns=("Название", "Тип", "Дата поступления", "Дата списания", "Количество", "Детали"), show="headings")
        self.tree.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        # Настраиваем колонки
        columns = [
            ("Название", 200),
            ("Тип", 100),
            ("Дата поступления", 150),
            ("Дата списания", 150),
            ("Количество", 80),
            ("Детали", 400)
        ]

        for col_name, width in columns:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width, anchor=tk.W)

        # Загружаем данные
        self.load_data()
        self.update_table()

    def load_data(self):
        try:
            self.products = parse_json(self.filename)
        except Exception as e:
            messagebox.showerror("Error", f"Ошибка загрузки данных: {str(e)}")

    def save_data(self):
        data = {}
        for idx, product in enumerate(self.products):
            item_data = {
                "name": product.name,
                "date_of_receipt": product.formated_date_of_receipt,
                "count": product.count
            }

            # Добавляем дату списания если есть
            if product.date_of_write_off:
                item_data["date_of_write_off"] = product.formated_date_of_write_off

            if isinstance(product, Clothing):
                item_data.update({
                    "size": product.size,
                    "color": product.color,
                    "material": product.material
                })
            elif isinstance(product, Furniture):
                item_data.update({
                    "material": product.material,
                    "dimensions": product.dimensions,
                    "weight": product.weight
                })

            data[f"Prod{idx + 1}"] = item_data

        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Данные успешно сохранены")
        except Exception as e:
            messagebox.showerror("Error", f"Ошибка сохранения данных: {str(e)}")

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for product in self.products:
            details = ""
            product_type = "Base Product"

            if isinstance(product, Clothing):
                product_type = "Clothing"
                details = f"Size: {product.size}, Color: {product.color}, Material: {product.material}"
            elif isinstance(product, Furniture):
                product_type = "Furniture"
                details = f"Material: {product.material}, Dimensions: {product.dimensions}, Weight: {product.weight}"

            # Добавляем колонку с датой списания
            self.tree.insert("", tk.END, values=(
                product.name,
                product_type,
                product.formated_date_of_receipt,
                product.formated_date_of_write_off,
                product.count,
                details
            ))

    def write_off_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Продукт не выбран")
            return

        index = self.tree.index(selected[0])
        product = self.products[index]

        # Диалог для ввода даты
        date_str = simpledialog.askstring("Списание",
                                          "Введите дату списания:",
                                          parent=self.master)

        if date_str:
            try:
                set_write_off_date(product, date_str)
                self.update_table()
            except ValidationError as e:
                messagebox.showerror("Error", str(e))

    def add_product(self):
        # Диалоговое окно для выбора типа продукта
        class TypeChoiceDialog(tk.Toplevel):
            def __init__(self, parent):
                super().__init__(parent)
                self.parent = parent
                self.result = None  # Результат выбора пользователя
                self.create_widgets()

            def create_widgets(self):
                # Заголовок
                ttk.Label(self, text="Выберите тип продукта:").pack(pady=10)

                # Выпадающий список с типами продуктов
                self.type_var = tk.StringVar()
                self.combobox = ttk.Combobox(
                    self,
                    textvariable=self.type_var,
                    values=["Base", "Clothing", "Furniture"],  # Доступные типы
                    state="readonly"  # Запрет на ручной ввод
                )
                self.combobox.pack(padx=20, pady=5)
                self.combobox.current(0)  # Выбираем первый тип по умолчанию

                # Кнопки управления
                btn_frame = ttk.Frame(self)
                btn_frame.pack(pady=10)

                ttk.Button(btn_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Отмена", command=self.cancel).pack(side=tk.RIGHT, padx=5)

            def ok(self):

                self.result = self.type_var.get()  # Сохраняем выбранный тип
                self.destroy()

            def cancel(self):

                self.result = None
                self.destroy()

        type_dialog = TypeChoiceDialog(self.master)
        self.master.wait_window(type_dialog)

        if not type_dialog.result:
            return

        product_type = type_dialog.result

        class InputDialog(tk.Toplevel):
            def __init__(self, parent, fields):
                super().__init__(parent)
                self.parent = parent
                self.fields = fields
                self.entries = {}  # Хранит поля ввода
                self.result = None  # Результат ввода
                self.create_widgets()

            def create_widgets(self):
                # Создаем поля ввода для каждого параметра
                for i, field in enumerate(self.fields):
                    ttk.Label(self, text=f"{field}:").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
                    entry = ttk.Entry(self)
                    entry.grid(row=i, column=1, padx=5, pady=2, sticky=tk.EW)
                    self.entries[field] = entry

                # Кнопка OK
                ttk.Button(self, text="OK", command=self.ok).grid(
                    row=len(self.fields), column=0, columnspan=2, pady=5
                )
                self.columnconfigure(1, weight=1)

            def ok(self):

                self.result = {field: entry.get() for field, entry in self.entries.items()}
                self.destroy()


        base_fields = ["Название", "Дата поступления (DD.MM.YYYY)", "Количество"]
        fields_map = {
            "Base": base_fields,
            "Clothing": base_fields + ["Размер", "Цвет", "Материал"],
            "Furniture": base_fields + ["Материал", "Размеры (WxLxH)", "Вес"]
        }


        dialog = InputDialog(self.master, fields_map[product_type])
        self.master.wait_window(dialog)


        if hasattr(dialog, 'result'):
            data = {}
            try:

                for key, value in dialog.result.items():
                    clean_key = key.split()[0]
                    if clean_key == "count" or clean_key == "weight":
                        data[clean_key] = int(value)
                    else:
                        data[clean_key] = value

                if product_type == "Clothing":
                    new_product = Clothing(data)
                elif product_type == "Furniture":
                    new_product = Furniture(data)
                else:
                    new_product = BaseProduct(data)

                self.products.append(new_product)
                self.update_table()

            except ValidationError as e:
                messagebox.showerror("Validation Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Ошибка создания продукта: {str(e)}")

    def remove_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Не выбран продукт")
            return

        index = self.tree.index(selected[0])
        del self.products[index]
        self.update_table()

class ValidationError(Exception):
    pass

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

        self.date_of_write_off = None

    @property
    def formated_date_of_receipt(self):
        return self.date_of_receipt.strftime('%d.%m.%Y')

    @property
    def formated_date_of_write_off(self):
        if self.date_of_write_off:
            return self.date_of_write_off.strftime('%d.%m.%Y')
        return "Не списано"

    def __repr__(self):
        return f"<BaseProduct name={self.name}, date={self.formated_date_of_receipt}, count={self.count}, write_off_date={self.formated_date_of_write_off}>"

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
            lenght = int(dimensions_parts[1])
            height = int(dimensions_parts[2])
        except:
            raise ValidationError("Размеры должны быть только числами")
        if width <= 0 or lenght <=0 or height <= 0:
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


if __name__ == "__main__":
    root = tk.Tk()
    app = UI(root, "example.json")
    root.mainloop()
