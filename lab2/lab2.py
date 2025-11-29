import os
import json
from enum import Enum
from typing import Dict, List, Tuple, Optional


class Color(Enum):
    """Перечисление для цветов текста"""
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    DEFAULT = 39


class Printer:
    """
    Класс для вывода текста в консоль с использованием ANSI escape sequences
    и псевдошрифтов из файлов
    """

    # ANSI escape sequences как константы класса
    RESET = '\033[0m'
    CLEAR_SCREEN = '\033[2J'
    CURSOR_HOME = '\033[H'

    # Словарь для хранения загруженных шрифтов
    _fonts: Dict[str, Dict[str, List[str]]] = {}

    def __init__(self, color: Color = Color.DEFAULT,
                 position: Tuple[int, int] = (0, 0),
                 symbol: str = '*',
                 font_file: str = 'font5.json'):
        """
        Инициализация экземпляра принтера

        Args:
            color: Цвет текста
            position: Начальная позиция (x, y)
            symbol: Символ для отрисовки псевдошрифта
            font_file: Файл с описанием шрифта
        """
        self.color = color
        self.position = position
        self.symbol = symbol
        self.font_file = font_file
        self._original_position = position
        self._load_font_if_needed(font_file)

    def __enter__(self): #
        """Вызывается при входе в контекстный менеджер with"""
        self._save_cursor_position()
        self._move_cursor(*self.position)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):#
        """Вызывается при выходе из контекстного менеджера with"""
        self._restore_cursor_position()
        print(self.RESET)  # Сброс цвета

    @classmethod
    def _load_font(cls, font_file: str) -> Dict[str, List[str]]:
        """
        Загрузка шрифта из JSON файла

        Args:
            font_file: Имя файла со шрифтом

        Returns:
            Словарь с описанием символов шрифта
        """
        try:
            with open(font_file, 'r', encoding='utf-8') as f:
                font_data = json.load(f)
            cls._fonts[font_file] = font_data
            return font_data
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл шрифта '{font_file}' не найден")
        except json.JSONDecodeError:
            raise ValueError(f"Некорректный формат файла '{font_file}'")

    def _load_font_if_needed(self, font_file: str):
        """Загрузка шрифта, если он еще не загружен"""
        if font_file not in self._fonts:
            self._load_font(font_file)

    @classmethod
    def _get_ansi_color(cls, color: Color) -> str:
        """
        Получение ANSI escape sequence для цвета

        Args:
            color: Цвет из перечисления

        Returns:
            ANSI escape sequence
        """
        return f'\033[{color.value}m'

    def _move_cursor(self, x: int, y: int):
        """
        Перемещение курсора в указанную позицию

        Args:
            x: Координата по горизонтали
            y: Координата по вертикали
        """
        print(f'\033[{y + 1};{x + 1}H', end='')

    def _save_cursor_position(self):
        """Сохранение текущей позиции курсора"""
        print('\033[s', end='')

    def _restore_cursor_position(self):
        """Восстановление сохраненной позиции курсора"""
        print('\033[u', end='')

    def _get_char_pattern(self, char: str) -> List[str]:
        """
        Получение шаблона для символа из загруженного шрифта

        Args:
            char: Символ для отрисовки

        Returns:
            Список строк, представляющих шаблон символа
        """
        char_upper = char.upper()
        font_data = self._fonts[self.font_file]

        if char_upper in font_data:
            return font_data[char_upper]
        elif char == ' ':
            # Для пробела возвращаем пустой шаблон
            height = len(font_data.get('A', ['']))
            return [''] * height
        else:
            # Если символ не найден, используем заглавную версию или возвращаем пустой шаблон
            return font_data.get(char_upper, [''])

    def _render_char(self, char: str, start_x: int, start_y: int):
        """
        Отрисовка одного символа в указанной позиции

        Args:
            char: Символ для отрисовки
            start_x: Начальная позиция по X
            start_y: Начальная позиция по Y
        """
        pattern = self._get_char_pattern(char)

        for i, line in enumerate(pattern):
            # Заменяем символы в шаблоне на указанный символ отрисовки
            rendered_line = line.replace('#', self.symbol).replace('*', self.symbol)
            if rendered_line.strip():  # Если строка не пустая
                self._move_cursor(start_x, start_y + i)
                print(rendered_line)

    @classmethod
    def print_text(cls, text: str, color: Color = Color.DEFAULT,
                   position: Tuple[int, int] = (0, 0), symbol: str = '*',
                   font_file: str = 'font5.json'):
        """
        Статический метод для вывода текста

        Args:
            text: Текст для вывода
            color: Цвет текста
            position: Позиция вывода (x, y)
            symbol: Символ для отрисовки
            font_file: Файл с описанием шрифта
        """
        # Создаем временный экземпляр для вывода
        with cls(color, position, symbol, font_file) as printer:
            printer.print(text)

    def print(self, text: str):
        """
        Вывод текста с использованием текущих настроек принтера

        Args:
            text: Текст для вывода
        """
        x, y = self.position
        current_x, current_y = x, y

        # Устанавливаем цвет
        print(self._get_ansi_color(self.color), end='')

        for char in text:
            if char == '\n':
                # Переход на новую строку
                char_pattern = self._get_char_pattern('A')
                current_y += len(char_pattern) + 1 if char_pattern else 6  # Высота символа + отступ
                current_x = x
            else:
                # Отрисовка символа
                self._render_char(char, current_x, current_y)
                # Смещаем позицию для следующего символа
                char_pattern = self._get_char_pattern(char)
                if char_pattern:
                    current_x += max(len(line) for line in char_pattern) + 1  # Ширина + отступ
                else:
                    current_x += 6  # Стандартный отступ если символ не найден

        # Обновляем текущую позицию
        self.position = (current_x, current_y)


# Демонстрация работы
def demonstrate_printer():
    """Демонстрация работы класса Printer"""

    # Очистка экрана
    print(Printer.CLEAR_SCREEN, end='')

    print("=== ДЕМОНСТРАЦИЯ РАБОТЫ КЛАССА PRINTER ===\n")

    # 1. Статическое использование

    Printer.print_text("HELLO", Color.RED, (0, 2), '#', 'font5.json')
    Printer.print_text("WORLD", Color.GREEN, (30, 2), '@', 'font5.json')

    # 2. Использование с контекстным менеджером

    with Printer(Color.CYAN, (0,10), '$', 'font5.json') as printer:
        printer.print("PYTHON")
        printer.print(" IS COOL")

    # 3. Демонстрация независимости от шрифта


    # Шрифт высотой 5 символов
    with Printer(Color.YELLOW, (0, 18), '*', 'font5.json') as printer:
        printer.print("FONT five")

    # Шрифт высотой 7 символов
    with Printer(Color.MAGENTA, (13, 25), '+', 'font7.json') as printer:
        printer.print("abcde")

    # 4. Разные цвета и символы

    colors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.MAGENTA, ]
    symbols = ['■', '●', '▲', '♦', '♥']

    for i, (color, symbol) in enumerate(zip(colors, symbols)):

        Printer.print_text(f"COLOR{i+1}", color, ( i*35, 35), symbol, 'font5.json')

    # Перемещаем курсор вниз после вывода
    print(f'\033[50;1H')  # Перемещение курсора в позицию (1, 50)
    print("Демонстрация завершена!")


if __name__ == "__main__":
    demonstrate_printer()