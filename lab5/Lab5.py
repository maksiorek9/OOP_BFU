from dataclasses import dataclass, field
from typing import Optional, Sequence, TypeVar, Generic,Dict, Any, Type
from abc import ABC, abstractmethod
import json
import os

@dataclass(order=True)
class User:
    """Класс пользователя с автоматической сортировкой по полю name"""
    # Поле для сортировки должно быть первым при order=True
    name: str = field(compare=False)  # compare=False - исключаем из сравнения для порядка
    id: int = field(default=0, compare=False)
    login: str = field(default="", compare=False)
    password: str = field(default="", repr=False, compare=False)  # repr=False - скрываем в строковом представлении
    email: Optional[str] = field(default=None, compare=False)
    address: Optional[str] = field(default=None, compare=False)
    
    def __post_init__(self):
        """Вызывается после инициализации, гарантируем что id установлен"""
        if self.id == 0:
            # В реальной системе id генерировался бы репозиторием
            self.id = id(self)

T = TypeVar('T')# показывет что Т может содержать что угодно

class IDataRepository(ABC, Generic[T]):
    """Интерфейс для CRUD операций с любым типом данных"""
    
    @abstractmethod
    def get_all(self) -> Sequence[T]:
        """Получить все записи"""
        ...
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Найти запись по ID"""
        ...
    
    @abstractmethod
    def add(self, item: T) -> None:
        """Добавить новую запись"""
        ...
    
    @abstractmethod
    def update(self, item: T) -> None:
        """Обновить существующую запись"""
        ...
    
    @abstractmethod
    def delete(self, item: T) -> None:
        """Удалить запись"""
        ...


class IUserRepository(IDataRepository[User]):
    """Специализированный интерфейс для работы с пользователями"""
    
    @abstractmethod
    def get_by_login(self, login: str) -> Optional[User]:
        """Найти пользователя по логину"""
        ...


class JsonDataRepository(IDataRepository[T]):
    """Реализация репозитория с хранением данных в JSON файле"""
    
    def __init__(self, file_path: str, data_class: Type[T]):
        """
        Args:
            file_path: путь к файлу для хранения данных
            data_class: класс данных для десериализации
        """
        self.file_path = file_path
        self.data_class = data_class
        self._data: Dict[int, T] = {}
        self._next_id = 1
        self._load_data()
    
    def _load_data(self) -> None:
        """Загрузить данные из файла"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
                    for item_data in data_list:
                        # Создаем объект из словаря
                        item = self._dict_to_obj(item_data)
                        self._data[item.id] = item
                        if item.id >= self._next_id:
                            self._next_id = item.id + 1
            except (json.JSONDecodeError, KeyError):
                self._data = {}
    
    def _save_data(self) -> None:
        """Сохранить данные в файл"""
        data_list = [self._obj_to_dict(item) for item in self._data.values()]
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=2, ensure_ascii=False)
    
    def _obj_to_dict(self, obj: T) -> Dict[str, Any]:
        """Преобразовать объект в словарь для JSON"""
        return obj.__dict__.copy()
    
    def _dict_to_obj(self, data: Dict[str, Any]) -> T:
        """Преобразовать словарь в объект"""
        return self.data_class(**data)
    
    def get_all(self) -> Sequence[T]:
        """Получить все записи"""
        return list(self._data.values())
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Найти запись по ID"""
        return self._data.get(id)
    
    def add(self, item: T) -> None:
        """Добавить новую запись"""
        if item.id == 0:
            item.id = self._next_id
            self._next_id += 1
        self._data[item.id] = item
        self._save_data()
    
    def update(self, item: T) -> None:
        """Обновить существующую запись"""
        if item.id in self._data:
            self._data[item.id] = item
            self._save_data()
    
    def delete(self, item: T) -> None:
        """Удалить запись"""
        if item.id in self._data:
            del self._data[item.id]
            self._save_data()

class UserRepository(JsonDataRepository[User], IUserRepository):
    """Реализация репозитория пользователей на основе JSON хранилища"""
    
    def __init__(self, file_path: str = "users.json"):
        super().__init__(file_path, User)
    
    def get_by_login(self, login: str) -> Optional[User]:
        """Найти пользователя по логину"""
        for user in self._data.values():
            if user.login == login:
                return user
        return None
class IAuthService(ABC):
    """Интерфейс сервиса авторизации"""
    
    @abstractmethod
    def sign_in(self, user: User) -> None:
        """Вход пользователя в систему"""
        ...
    
    @abstractmethod
    def sign_out(self) -> None:
        """Выход пользователя из системы"""
        ...
    
    @property
    @abstractmethod
    def is_authorized(self) -> bool:
        """Проверка авторизации пользователя"""
        ...
    
    @property
    @abstractmethod
    def current_user(self) -> Optional[User]:
        """Получить текущего пользователя"""
        ...
class PersistentAuthService(IAuthService):
    """Сервис авторизации с сохранением состояния в файле""" 
    def __init__(self, user_repository: IUserRepository, auth_file: str = "auth_state.json"):
        self.user_repository = user_repository
        self.auth_file = auth_file
        self._current_user: Optional[User] = None
        self._auto_login()
    
    def _auto_login(self) -> None:
        """Автоматическая авторизация при запуске"""
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'r', encoding='utf-8') as f:
                    auth_data = json.load(f)
                    user_id = auth_data.get('user_id')
                    if user_id:
                        user = self.user_repository.get_by_id(user_id)
                        if user:
                            self._current_user = user
                            print(f"Автоматически авторизован пользователь: {user.name}")
            except (json.JSONDecodeError, KeyError):
                ...
    
    def _save_auth_state(self) -> None:
        """Сохранить состояние авторизации"""
        auth_data = {'user_id': self._current_user.id if self._current_user else None}
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f)
    
    def sign_in(self, user: User) -> None:
        """Вход пользователя в систему"""
        self._current_user = user
        self._save_auth_state()
        print(f"Пользователь {user.name} успешно авторизован")
    
    def sign_out(self) -> None:
        """Выход пользователя из системы"""
        if self._current_user:
            print(f"Пользователь {self._current_user.name} вышел из системы")
            self._current_user = None
            self._save_auth_state()
    
    @property
    def is_authorized(self) -> bool:
        """Проверка авторизации пользователя"""
        return self._current_user is not None
    
    @property
    def current_user(self) -> Optional[User]:
        """Получить текущего пользователя"""
        return self._current_user
def demonstrate_system():
    """Демонстрация работы всей системы"""
    
    print("=== СИСТЕМА АВТОРИЗАЦИИ И ХРАНЕНИЯ ПОЛЬЗОВАТЕЛЕЙ ===\n")
    
    # Создаем репозиторий и сервис авторизации
    user_repo = UserRepository()
    auth_service = PersistentAuthService(user_repo)
    
    # 1. Добавление пользователей
    print("1. ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ")
    users = [
        User(name="Иван Иванов", login="ivanov", password="pass123", email="ivan@mail.ru"),
        User(name="Петр Петров", login="petrov", password="qwerty", email="petr@gmail.com", address="Москва"),
        User(name="Анна Сидорова", login="sidorova", password="anna123")
    ]
    
    for user in users:
        user_repo.add(user)
        print(f"   Добавлен: {user}")
    print(f"\n   Всего пользователей: {len(user_repo.get_all())}")
    
    # 2. Сортировка пользователей по имени
    print("\n2. СОРТИРОВКА ПОЛЬЗОВАТЕЛЕЙ ПО ИМЕНИ")
    sorted_users = sorted(user_repo.get_all())
    for user in sorted_users:
        print(f"   {user.name} (логин: {user.login})")
        
    # 3. Авторизация пользователя
    print("\n3. АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ")
    user = user_repo.get_by_login("ivanov")
    if user:
        auth_service.sign_in(user)
        print(f"   Текущий пользователь: {auth_service.current_user.name}")
        print(f"   Авторизован: {auth_service.is_authorized}")
    
    # 4. Редактирование пользователя
    print("\n4. РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ")
    if user:
        user.email = "new_ivan@mail.ru"
        user_repo.update(user)
        print(f"   Обновлен email пользователя: {user_repo.get_by_id(user.id)}")
    
    # 5. Смена пользователя
    print("\n5. СМЕНА ПОЛЬЗОВАТЕЛЯ")
    new_user = user_repo.get_by_login("sidorova")
    if new_user:
        auth_service.sign_in(new_user)
        print(f"   Новый текущий пользователь: {auth_service.current_user.name}")
    
    # 6. Выход из системы
    print("\n6. ВЫХОД ИЗ СИСТЕМЫ")
    auth_service.sign_out()
    print(f"   Авторизован: {auth_service.is_authorized}")
    
    # 7. Демонстрация поиска
    print("\n7. ПОИСК ПОЛЬЗОВАТЕЛЕЙ")
    found_user = user_repo.get_by_login("petrov")
    if found_user:
        print(f"   Найден пользователь: {found_user}")
    
    # 8. Удаление пользователя
    print("\n8. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ")
    user_to_delete = user_repo.get_by_login("sidorova")
    if user_to_delete:
        user_repo.delete(user_to_delete)
        print(f"   Пользователь удален. Всего пользователей: {len(user_repo.get_all())}")


def demonstrate_auto_login():
    """Демонстрация автоматической авторизации при повторном запуске"""
    print("\n=== ДЕМОНСТРАЦИЯ АВТОМАТИЧЕСКОЙ АВТОРИЗАЦИИ ===")
    
    # Первый запуск - авторизуем пользователя
    user_repo = UserRepository()
    auth_service = PersistentAuthService(user_repo)
    
    user = user_repo.get_by_login("ivanov")
    if user:
        auth_service.sign_in(user)
        print(f"Пользователь авторизован: {auth_service.current_user.name}")
    
    # "Перезапуск" системы - создаем новые экземпляры
    print("\n--- Перезапуск системы ---")
    new_user_repo = UserRepository()
    new_auth_service = PersistentAuthService(new_user_repo)
    
    print(f"Автоматически авторизован: {new_auth_service.is_authorized}")
    if new_auth_service.is_authorized:
        print(f"Текущий пользователь: {new_auth_service.current_user.name}")


if __name__ == "__main__":
    # Очистка файлов для демонстрации
    for file in ["users.json", "auth_state.json"]:
        if os.path.exists(file):
            os.remove(file)
    demonstrate_system()
    demonstrate_auto_login()