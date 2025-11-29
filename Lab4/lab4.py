# Лабораторная работа 4 (валидация и автообновление через события)
#
# Реализуем паттерн Broadcaster/receiver или observer, симулируем событийное программирование.
# 1. Создать протокол/интерфейс EventHandler<TEventArgs>
#  - handle(sender: object (or Any), args: TEventArgs) для обработки события
# где TEventArgs - произвольный тип данных
#
# 2. Создать класс Event, который реализует механизм подписки и отписки от события, а также оповещение всех подписантов
#   - "+=" (handler: EventHandler<TEventArgs>) - подписка на событие
#   - "-="  (handler: EventHandler<TEventArgs>)  - отписка от события
#   - invoke(sender: T,  args: TEventArgs) (в Python можно вместо нее или дополнительно использовать call) - запускает оповещение всех подписантов
#
# 3. Создать класс PropertyChangedEventArgs(EventArgs)
#   - свойство property_name: str
#
# 4. Создать класс реализующий EventHandler<PropertyChangedEventArgs>, обрабатывающий событие и выводящий информацию в консоль
#
# 5. Создать класс PropertyChangingEventArgs(EventArgs)
#   - свойство property_name: str
#   - свойство old_value: Any
#   - свойство new_value: Any
#   - свойство can_change: bool
#
# 6. Создать класс реализующий EventHandler<PropertyChangingEventArgs>, обрабатывающий событие и работающий как валидатор при попытке изменения свйоства.
# Для отмены измененения используйте свйоство can_change
#
# 7. Создать не менее двух классов, каждый из которых имеет не менее трех полей, которые при изменении свойств вызывают событие от EventHandler<PropertyChangedEventArgs> после изменения свойства и
# EventHandler<PropertyChangingEventArgs> до изменения значения свойства с возможностью отменить изменение



from typing import Any, Callable, List, Optional

# 1. Интерфейс EventHandler
class EventHandler:
    def handle(self, sender: Any, args: Any) -> None:
        raise NotImplementedError()

# 2. Класс Event для управления подписками
class Event:
    def __init__(self):
        self._handlers: List[EventHandler] = []
    
    def __iadd__(self, handler: EventHandler) -> 'Event':
        """Оператор += для подписки"""
        if handler not in self._handlers:
            self._handlers.append(handler)
        return self
    
    def __isub__(self, handler: EventHandler) -> 'Event':
        """Оператор -= для отписки"""
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self
    
    def __call__(self, sender: Any, args: Any) -> None:
        """Вызов события - оповещение всех подписчиков"""
        self.invoke(sender, args)
    
    def invoke(self, sender: Any, args: Any) -> None:
        """Запуск оповещения всех подписчиков"""
        for handler in self._handlers[:]:  # Копируем список на случай изменений во время обработки
            handler.handle(sender, args)

# 3. Базовый класс для аргументов события
class EventArgs:
    pass

# 4. PropertyChangedEventArgs - после изменения свойства
class PropertyChangedEventArgs(EventArgs):
    def __init__(self, property_name: str):
        self.property_name = property_name
    
    def __str__(self):
        return f"PropertyChanged: {self.property_name}"

# 5. PropertyChangingEventArgs - до изменения свойства (с валидацией)
class PropertyChangingEventArgs(EventArgs):
    def __init__(self, property_name: str, old_value: Any, new_value: Any):
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.can_change = True
    
    def __str__(self):
        return f"PropertyChanging: {self.property_name} from {self.old_value} to {self.new_value}"

# 6. Обработчик для PropertyChangedEventArgs (вывод в консоль)
class PropertyChangedHandler(EventHandler):
    def handle(self, sender: Any, args: PropertyChangedEventArgs) -> None:
        print(f"[PropertyChangedHandler] {sender.__class__.__name__}: {args}")

# 7. Валидатор для PropertyChangingEventArgs
class PropertyChangingValidator(EventHandler):
    def handle(self, sender: Any, args: PropertyChangingEventArgs) -> None:
        print(f"[PropertyChangingValidator] {sender.__class__.__name__}: {args}")
        
        # Примеры валидации
        if args.property_name == "age" and isinstance(args.new_value, (int, float)):
            if args.new_value < 0:
                print("  ❌ Возраст не может быть отрицательным!")
                args.can_change = False
            elif args.new_value > 150:
                print("  ❌ Возраст не может быть больше 150!")
                args.can_change = False
        
        elif args.property_name == "email" and isinstance(args.new_value, str):
            if "@" not in args.new_value:
                print("  ❌ Email должен содержать символ @!")
                args.can_change = False
        
        elif args.property_name == "balance" and isinstance(args.new_value, (int, float)):
            if args.new_value < -1000:
                print("  ❌ Баланс не может быть меньше -1000!")
                args.can_change = False
        
        if args.can_change:
            print("  ✅ Изменение разрешено")
        else:
            print("  ❌ Изменение запрещено")

# Базовый класс с поддержкой событий
class ObservableObject:
    def __init__(self):
        self.property_changing = Event()
        self.property_changed = Event()

# 8. Класс User с событиями изменения свойств
class User(ObservableObject):
    def __init__(self, name: str = "", email: str = "", age: int = 0):
        super().__init__()
        self._name = name
        self._email = email
        self._age = age
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        if self._name != value:
            # Событие до изменения (валидация)
            changing_args = PropertyChangingEventArgs("name", self._name, value)
            self.property_changing(self, changing_args)
            
            if changing_args.can_change:
                old_value = self._name
                self._name = value
                # Событие после изменения
                self.property_changed(self, PropertyChangedEventArgs("name"))
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        if self._email != value:
            # Событие до изменения (валидация)
            changing_args = PropertyChangingEventArgs("email", self._email, value)
            self.property_changing(self, changing_args)
            
            if changing_args.can_change:
                old_value = self._email
                self._email = value
                # Событие после изменения
                self.property_changed(self, PropertyChangedEventArgs("email"))
    
    @property
    def age(self) -> int:
        return self._age
    
    @age.setter
    def age(self, value: int) -> None:
        if self._age != value:
            # Событие до изменения (валидация)
            changing_args = PropertyChangingEventArgs("age", self._age, value)
            self.property_changing(self, changing_args)
            
            if changing_args.can_change:
                old_value = self._age
                self._age = value
                # Событие после изменения
                self.property_changed(self, PropertyChangedEventArgs("age"))
    
    def __str__(self):
        return f"User(name='{self.name}', email='{self.email}', age={self.age})"

# 9. Класс Account с событиями изменения свойств
class Account(ObservableObject):
    def __init__(self, account_number: str = "", balance: float = 0.0, is_active: bool = True):
        super().__init__()
        self._account_number = account_number
        self._balance = balance
        self._is_active = is_active
    
    @property
    def account_number(self) -> str:
        return self._account_number
    
    @account_number.setter
    def account_number(self, value: str) -> None:
        if self._account_number != value:
            changing_args = PropertyChangingEventArgs("account_number", self._account_number, value)
            self.property_changing(self, changing_args)
            
            if changing_args.can_change:
                self._account_number = value
                self.property_changed(self, PropertyChangedEventArgs("account_number"))
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @balance.setter
    def balance(self, value: float) -> None:
        if self._balance != value:
            changing_args = PropertyChangingEventArgs("balance", self._balance, value)
            self.property_changing(self, changing_args)
            
            if changing_args.can_change:
                self._balance = value
                self.property_changed(self, PropertyChangedEventArgs("balance"))
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @is_active.setter
    def is_active(self, value: bool) -> None:
        if self._is_active != value:
            changing_args = PropertyChangingEventArgs("is_active", self._is_active, value)
            self.property_changing(self, changing_args)
            
            if changing_args.can_change:
                self._is_active = value
                self.property_changed(self, PropertyChangedEventArgs("is_active"))
    
    def __str__(self):
        return f"Account(number='{self.account_number}', balance={self.balance}, active={self.is_active})"

# Демонстрация работы
def main():
    print("=== Демонстрация паттерна Observer с валидацией ===\n")
    
    # Создаем обработчики
    changed_handler = PropertyChangedHandler()
    validator = PropertyChangingValidator()
    
    # Создаем объекты
    user = User("John", "john@example.com", 25)
    account = Account("123456", 1000.0, True)
    
    # Подписываемся на события
    user.property_changed += changed_handler
    user.property_changing += validator
    
    account.property_changed += changed_handler
    account.property_changing += validator
    
    print("=== Тестирование класса User ===")
    print(f"Начальное состояние: {user}")
    
    print("\n1. Корректное изменение возраста:")
    user.age = 30
    
    print("\n2. Некорректное изменение возраста (отрицательное):")
    user.age = -5
    
    print("\n3. Некорректное изменение возраста (слишком большое):")
    user.age = 200
    
    print("\n4. Корректное изменение email:")
    user.email = "john.doe@example.com"
    
    print("\n5. Некорректное изменение email:")
    user.email = "invalid-email"
    
    print(f"\nИтоговое состояние: {user}")
    
    print("\n=== Тестирование класса Account ===")
    print(f"Начальное состояние: {account}")
    
    print("\n1. Корректное изменение баланса:")
    account.balance = 1500.0
    
    print("\n2. Некорректное изменение баланса:")
    account.balance = -2000.0
    
    print("\n3. Изменение статуса аккаунта:")
    account.is_active = False
    
    print(f"\nИтоговое состояние: {account}")
    
    # Отписка от событий
    print("\n=== Отписка от событий ===")
    user.property_changed -= changed_handler
    user.property_changing -= validator
    
    print("Изменение после отписки (сообщений не должно быть):")
    user.age = 35
    print(f"Результат: {user}")

if __name__ == "__main__":
    main()