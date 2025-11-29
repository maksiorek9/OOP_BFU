from logging import Logger
import re
import datetime
import socket
import ftplib
from abc import ABC, abstractmethod 
import sys

from enum import Enum, Flag, auto
from typing import List, Set, Dict, Any, Optional

class LogLevel(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3


class TimeComponent(Flag):
    NOTHING = 0#
    YEAR = 1
    MONTH = 2#нумератор#2
    DAY = 4#3
    HOUR = 8#4
    MINUTE = 16#5
    SECOND = 32#6
    MICROSECOND = 64#7
    WEEKDAY = 128#8
    
    # Предустановленные комбинации
    DATE_ONLY = YEAR | MONTH | DAY # ну посчитать сложно 
    TIME_ONLY = HOUR | MINUTE | SECOND
    DATE_TIME = DATE_ONLY | TIME_ONLY
    FULL = DATE_TIME | MICROSECOND
    DEFAULT = DATE_TIME


# 2. Протокол фильтров
class LogFilterProtocol(ABC):
    @abstractmethod
    def match(self, log_level: LogLevel, text: str) -> bool:
        ...

# 3. Реализации фильтров
class SimpleLogFilter(LogFilterProtocol):
    def __init__(self, pattern: str):
        self.pattern = pattern.lower()#исключения

    def match(self, log_level: LogLevel, text: str) -> bool:
        return self.pattern in text.lower()


class ReLogFilter(LogFilterProtocol):
    def __init__(self, pattern: str):
        try:
            self.pattern = re.compile(pattern)
        except:
            print("error pat")

    def match(self, log_level: LogLevel, text: str) -> bool:
        return bool(self.pattern.search(text))


class LevelFilter(LogFilterProtocol):
    def __init__(self, min_level: LogLevel):
        self.min_level = min_level

    def match(self, log_level: LogLevel, text: str) -> bool:
        return log_level.value >= self.min_level.value


# 4. Протокол обработчиков
class LogHandlerProtocol:
    def handle(self, log_level: LogLevel, text: str) -> None:
        raise NotImplementedError

class ConsoleHandler(LogHandlerProtocol):
    def handle(self, log_level: LogLevel, text: str) -> None:
        print(text)

# 6. Протокол форматтеров
class LogFormatterProtocol(ABC):
    @abstractmethod
    def format(self, log_level: LogLevel, text: str, day:str) -> str:
        ...

# 7. Реализация форматтера
class SmartTimeFormatter(LogFormatterProtocol):
    # Пресеты форматов времени
    TIME_PRESETS = {
        # Основные пресеты
        'год': TimeComponent.YEAR,
        'месяц': TimeComponent.MONTH,
        'день': TimeComponent.DAY,
        'время': TimeComponent.TIME_ONLY,
        'дата': TimeComponent.DATE_ONLY,
        'дата_время': TimeComponent.DATE_TIME,
        'полный': TimeComponent.FULL,
        'день_недели': TimeComponent.WEEKDAY,
        
        # Комбинированные пресеты
        'год_время': TimeComponent.YEAR | TimeComponent.TIME_ONLY,
        'месяц_год': TimeComponent.YEAR | TimeComponent.MONTH,
        'день_время': TimeComponent.DAY | TimeComponent.TIME_ONLY,
        'дата_деньнедели': TimeComponent.DATE_ONLY | TimeComponent.WEEKDAY,
        
        # Короткие алиасы
        'г': TimeComponent.YEAR,
        'м': TimeComponent.MONTH,
        'д': TimeComponent.DAY,
        'ч': TimeComponent.HOUR,
        'мин': TimeComponent.MINUTE,
        'сек': TimeComponent.SECOND,
    }
    
    COMPONENT_FORMATS = {
        TimeComponent.YEAR: "%Y",
        TimeComponent.MONTH: "%m",
        TimeComponent.DAY: "%d",
        TimeComponent.HOUR: "%H",
        TimeComponent.MINUTE: "%M",
        TimeComponent.SECOND: "%S",
        TimeComponent.MICROSECOND: "%f",
        TimeComponent.WEEKDAY: "%A",
    }
    
    
    
    def __init__(self, time_preset: str = "дата_время"):
        self.current_preset = time_preset
        self.time_components = self._parse_preset(time_preset)
    
    def _parse_preset(self, preset_str: str) -> TimeComponent:
        """Парсит строку с пресетами и возвращает комбинацию компонентов"""
        if not preset_str:
            return TimeComponent.DEFAULT
        
        components = TimeComponent.NOTHING
        parts = preset_str.lower().replace(' ', '_').split('_')
        
        for part in parts:
            if part in self.TIME_PRESETS:
                components |= self.TIME_PRESETS[part]
        
        # Если ничего не найдено, используем по умолчанию
        if components == TimeComponent.NOTHING:
            return TimeComponent.DEFAULT
        
        return components
    
    def set_time_format(self, preset_str: str):
        """Динамически меняет формат времени"""
        self.current_preset = preset_str
        self.time_components = self._parse_preset(preset_str)
    
    def _get_component_order(self) -> List[TimeComponent]:
        """Определяет порядок компонентов на основе текущего пресета"""
        base_order = [
            TimeComponent.WEEKDAY,
            TimeComponent.YEAR,
            TimeComponent.MONTH, 
            TimeComponent.DAY,
            TimeComponent.HOUR,
            TimeComponent.MINUTE,
            TimeComponent.SECOND,
            TimeComponent.MICROSECOND,
        ]
        
        # Фильтруем только те компоненты, которые используются
        return [comp for comp in base_order if comp in self.time_components]
    
    def _format_component(self, component: TimeComponent, dt: datetime.datetime) -> str:
        """Форматирует отдельный компонент времени"""
        if component not in self.time_components:
            return ""
        
        if component == TimeComponent.WEEKDAY:
            weekday = dt.strftime(self.COMPONENT_FORMATS[component])
            return self.WEEKDAY_ABBR.get(weekday, weekday)
        
        return dt.strftime(self.COMPONENT_FORMATS[component])
    
    def _build_timestamp(self, dt: datetime.datetime) -> str:# PRIVITE
        """Строит временную метку с разными разделителями для разных типов компонентов"""
        date_parts = []
        time_parts = []
        other_parts = []
        
        # Группируем компоненты по типам
        for component in self._get_component_order():
            part = self._format_component(component, dt)
            if not part:
                continue
                
            if component in [TimeComponent.YEAR, TimeComponent.MONTH, TimeComponent.DAY]:
                date_parts.append(part)
            elif component in [TimeComponent.HOUR, TimeComponent.MINUTE, TimeComponent.SECOND, TimeComponent.MICROSECOND]:
                time_parts.append(part)
            else:  # WEEKDAY и другие
                other_parts.append(part)
        
        # Собираем части с разными разделителями
        result_parts = []
        
        
        # Дата - разделитель "."
        if date_parts:
            result_parts.append(".".join(date_parts))
        
        # Время - разделитель ":"
        if time_parts:
            # Для микросекунд используем "." как разделитель от секунд
            if TimeComponent.MICROSECOND in self.time_components and len(time_parts) > 3:
                # Разделяем основное время и микросекунды
                main_time = ":".join(time_parts[:3])  # часы:минуты:секунды
                microseconds = time_parts[3]  # микросекунды
                time_str = f"{main_time}.{microseconds}"
                result_parts.append(time_str)
            else:
                result_parts.append(":".join(time_parts))
        
        # Объединяем все части пробелом
        return " ".join(result_parts)
    
    def format(self, log_level: LogLevel, text: str) -> str:
        dt = datetime.datetime.now()
        timestamp = self._build_timestamp(dt)
        return f"[{log_level.name}] [{timestamp}] {text}"

# 8. Реализации обработчиков
class ConsoleHandler(LogHandlerProtocol):
    def handle(self, log_level: LogLevel, text: str) -> None:
        print(text)

class FileHandler(LogHandlerProtocol):
    def __init__(self, filename: str):
        self.filename = filename
    
    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
        except:
            print("error fale")
class SyslogHandler(LogHandlerProtocol):
    def __init__(self, host: str = 'localhost', port: int = 514):
        self.host = host
        self.port = port
    
    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                message = f"[{log_level.name}] {text}"
                s.sendto(message.encode('utf-8'), (self.host, self.port))
        except:
            print("syslog error")


class FtpHandler(LogHandlerProtocol):
    def __init__(self, host: str, username: str, password: str, remote_path: str = "/logs/"):
        self.host = host
        self.username = username
        self.password = password
        self.remote_path = remote_path
    
    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            # Просто выводим имитацию FTP отправки
            print(f"FTP: {text}")
        except:
            print("ftp error")


# 9. Расширенный класс Logger с поддержкой динамического формата
class DynamicLogger:
    def __init__(self, filters: list, formatters: list, handlers: list):
        self.filters = filters
        self.formatters = formatters
        self.handlers = handlers
    
    def log(self, log_level: LogLevel, text: str, time_format: str = None) -> None:
        # Применяем фильтры
        for filter_obj in self.filters:
            if not filter_obj.match(log_level, text):
                return
        
        # Динамически настраиваем форматтеры, если указан time_format
        formatted_text = text
        for formatter in self.formatters:
            if time_format and isinstance(formatter, SmartTimeFormatter):
                # Сохраняем текущий пресет
                original_preset = formatter.current_preset
                # Временно меняем формат
                formatter.set_time_format(time_format)
                formatted_text = formatter.format(log_level, formatted_text)
                # Возвращаем оригинальный пресет
                formatter.set_time_format(original_preset)
            else:
                formatted_text = formatter.format(log_level, formatted_text)
        
        # Передаем обработчикам
        for handler in self.handlers:
            handler.handle(log_level, formatted_text)
    
    def log_info(self, text: str, time_format: str = None) -> None:
        self.log(LogLevel.INFO, text, time_format)
    
    def log_warn(self, text: str, time_format: str = None) -> None:
        self.log(LogLevel.WARN, text, time_format)
    
    def log_error(self, text: str, time_format: str = None) -> None:
        self.log(LogLevel.ERROR, text, time_format)
    
    

# Пример использования в веб-приложении
class WebApplication:
    def __init__(self):
        # Настраиваем разные логгеры для разных целей
        smart_formatter = SmartTimeFormatter("дата_время")
        
        # Создаем логгеры для разных целей с новыми хендлерами
        self.access_logger = DynamicLogger(
            filters=[ReLogFilter("e")],
            formatters=[smart_formatter],
            handlers=[
                ConsoleHandler(), 
                FileHandler("access.log"),
                 # Добавили сокет
            ]
        )
        
        self.error_logger = DynamicLogger(
            filters=[LevelFilter(LogLevel.ERROR)],
            formatters=[smart_formatter],
            handlers=[
                ConsoleHandler(), 
                FileHandler("errors.log"),
                SyslogHandler()  # Добавили syslog для ошибок
            ]
        )
        
        self.security_logger = DynamicLogger(
            filters=[ReLogFilter("gfdhgjdhfgjdk")],
            formatters=[smart_formatter],
            handlers=[
                FileHandler("security.log"),
                FtpHandler("backup-server", "admin", "pass")  # Добавили FTP для бэкапа
            ]
        )

    def handle_request(self, user_id: int, endpoint: str, time_format: str = None):
        # Логируем доступ
        self.access_logger.log_info(
            f"Пользователь {user_id} запросил {endpoint}", 
            time_format
        )
        
        # Логируем события авторизации
        if user_id > 0:
            self.security_logger.log_info(
                f"Авторизация пользователя {user_id} для {endpoint}",
                "время"  # Для безопасности важно точное время
            )
        
        # Имитируем обработку запроса
        if user_id == 0:
            self.error_logger.log_error(
                f"Невалидный пользователь для {endpoint}",
                time_format
            )
            return False
        elif "admin" in endpoint and user_id != 1:
            self.error_logger.log_error(
                f"Неавторизованный доступ к админке: пользователь {user_id}",
                "полный"  # Полная информация для расследования
            )
            return False
        else:
            self.access_logger.log_info(
                f"Успешный ответ для {endpoint}",
                time_format
            ) 
            return True



# 9. Демонстрация работы
if __name__ == "__main__":
    # Создаем компоненты
    # Демонстрацияы
    

    print("=== Демонстрация системы логирования ===")

    app = WebApplication()
    app.handle_request(9000, "/api/users",'Полный')
    app.handle_request(0, "/api/admin","год_мин")
    
    print("=== Демонстрация завершена ===")


# Лабораторная работа 3 (Система логирования)
#
# Создать систему логирования, применяя композицию (агрегацию),
# с возможностью фильтрации и различных способов вывода информации.
# Использовать либо протоколы, либо интерфейсы, либо чисто абстрактные классы в зависимости от используемого языка программирования.
#
# 1. Создать перечислитель LogLevel со значениями INFO, WARN, ERROR
#  - LevelFilter - для фильтрации на основе перечислителя (его также создать )
#
# 2. Создать протокол/интерфейс фильтров ILogFilter / LogFilterProtocol:
#   - match(self, log_level: LogLevel, text: str) -> bool
#
# 3. Создать несколько классов реализующих данный протокол/интерфейс
#  - SimpleLogFilter - для фильтрации по вхождению паттерна, задаваемого текстом, в текст сообщения
#  - ReLogFilter - для фильтрации по вхождению паттерна, задаваемого регулярным выражением, в текст сообщения
#  - LevelFilter - Для фильтрации по LogLevel
#
# 4. Создать протокол/интерфейс обработчиков ILogHandler / LogHandlerProtocol:
#  - handle(self, log_level: LogLevel, text: str) -> None
#
# 5. Создать неcколько классов реализующих данный протокол/интерфейс
#  - FileHandler - для записи логов в файл
#  - SocketHandler - для отправки логов через сокет
#  - ConsoleHandler - для вывода логово в консоль
#  - SyslogHandler - для записи логов в системные логи
#  - FtpHandler - для записи логов на ftp сервер
#
# 6. Создать протокол/интерфейс обработчиков ILogFormatter / LogFormatterProtocol:
#  - format(self, log_level: LogLevel, text: str) -> str
#
# 7. Реализовать форматтер, который к каждому сообщению в логах добавляет данные по следующему формату:
# [<log_level>] [<data:yyyy.MM.dd hh:mm:ss>] <text>
# где <>  - плейсхолдеры, которые должны быть заменены на значения переменных
#
# 8. Реализовать класс Logger, который принимает
#   - список ILogFilter / LogFilterProtocol
#   - список  ILogFormatter / LogFormatterProtocol
#   - список ILogHandler / LogHandlerProtocol
#
#  и реализует:
#  - log(self, log_level: LogLevel, text: str) -> None - которая прогоняет логи через фильтры, потом последовательно через все форматтеры и отдает обработчикам
#  - log_info(text: str) -> None - записывает логи с LogLevel = LogLevel.INFO
#  - log_warn(text: str) -> None - записывает логи с LogLevel = LogLevel.WARN
#  - log_error(text: str) -> None - записывает логи с LogLevel = LogLevel.ERROR
#
#
# 9. Продемонстрировать работу спроектированной системы классов