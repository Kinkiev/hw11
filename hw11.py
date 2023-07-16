from collections import UserDict
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if not self.is_valid_phone(new_value):
            raise ValueError("Invalid phone number format")
        self._value = new_value

    @staticmethod
    def is_valid_phone(phone):
        if phone:
            if not phone.startswith("+380"):
                return False
            if len(phone) != 13:
                return False
            if not phone[4:].isdigit():
                return False
            return True
        return True


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if not self.is_valid_date(new_value):
            raise ValueError("Invalid date format")
        self._value = new_value

    @staticmethod
    def is_valid_date(birthday):
        try:
            datetime.datetime.strptime(birthday, "%d.%m.%Y")
            return True
        except ValueError:
            return False


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = name
        self.phones = []
        self.birthday = birthday
        if phone is not None:
            self.add_phone(phone)
        if birthday is not None:
            self.set_birthday(birthday)
    
    def add_phone(self, phone: Phone):
        if phone not in self.phones:
            self.phones.append(phone)
            return f"Phone {phone} added to contact {self.name}"
        return f"{phone} already added to {self.name}"

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def change_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if str(phone) == str(old_phone):
                self.phones[i] = new_phone
                break
            
    def set_birthday(self, birthday):
        try:
            self.birthday = datetime.strptime(birthday, "%d.%m.%Y").date()
            return f"Birthday set for {self.name}"
        except ValueError:
            return f"Invalid birthday format. Please use dd.mm.yyyy format."
            
    def days_to_birthday(self):
        if self.birthday is None:
            return "Birthday not set"
        
        current_date = datetime.now().date()
        next_birthday = datetime(current_date.year, self.birthday.month, self.birthday.day).date()
        
        if next_birthday < current_date: 
            next_birthday = datetime(current_date.year + 1, self.birthday.month, self.birthday.day).date()
            
        days_to_bd = (next_birthday - current_date).days
        return f"Days to next birthday for {self.name}: {days_to_bd}"

    def __str__(self):
        return f"Name: {self.name}, Phones: {', '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[str(record.name)] = record

    def remove_record(self, name):
        del self.data[str(name)]

    def search_by_name(self, name):
        results = []
        for record in self.data.values():
            if str(record.name) == name:
                results.append(record)
        return results

    def change_phone_by_name(self, name, new_phone):
        results = self.search_by_name(name)
        for result in results:
            result.change_phone(result.phones[0], Phone(new_phone))

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    
    def iterator(self, n=5):
        records = list(self.data.values())
        total_records = len(records)
        current_index = 0

        while current_index < total_records:
            yield records[current_index:current_index+n]
            current_index += n
            
    def show_all(self):
        iterator = self.iterator()
        for chunk in iterator:
            print("\n".join(str(record) for record in chunk))
            user_input = input("Press Enter to show more or q to quit: ")
            if user_input.lower() == 'q':
                break


def help() -> str:
    return "Available commands:\n" \
           "- hello\n" \
           "- add [name] [phone in format +380xxxxxxx]\n" \
           "- change [name] [phone]\n" \
           "- find [name]\n" \
           "- show_all\n" \
           "- show\n" \
           "- birthday [name] [date in format dd.mm.yyyy]\n" \
           "- days_to_bd [name]\n" \
           "- help \n" \
           "- bye, close, exit"


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "contact not found"
        except ValueError:
            return "invalid format, type help"
        except IndexError:
            return "Invalid input"
        except Exception:
            return help()

    return wrapper


ab = AddressBook()


def add(name: str, phone: str = None, birthday: str = None) -> str:
    try:
        record: Record = ab.get(str(name))
        if record:
            existing_phones = [str(p) for p in record.phones]
            if phone in existing_phones:
                return f"{phone} already added to {name}"
            new_phone = Phone(phone)
            return record.add_phone(new_phone)
        name_field = Name(name)
        phone_field = Phone(phone)
        birthday_field = Birthday(birthday) if birthday else None
        record = Record(name_field, phone_field, birthday_field)
        ab.add_record(record)
        return f"Contact {name} add success"
    except ValueError as e:
        return str(e)


@input_error
def find(name: str) -> str:
    results = ab.search_by_name(name)
    if results:
        return str(results[0])
    else:
        raise KeyError(f"Contact {name} not found")


@input_error
def change(name: str, new_phone: str) -> str:
    rec: Record = ab.get(str(name))
    if rec: 
        ab.change_phone_by_name(name, new_phone)
        return f"phone number for {name} updated"
    return f"no {name} in contacts"

@input_error
def show_all() -> str:
    ab.show_all()
    return ""

# @input_error
# def show_all() -> str:
#     if len(ab) == 0:
#         return "no contacts found"
#     else:
#         output = ""
#         for record in ab.values():
#             output += str(record) + "\n"
#         return output.strip()
    

@input_error
def set_birthday(name: str, birthday: str) -> str:
    rec: Record = ab.get(str(name))
    if rec:
        return rec.set_birthday(birthday)
    return f"No {name} in contacts"


@input_error
def days_to_birthday(name: str) -> str:
    rec: Record = ab.get(str(name))
    if rec:
        return rec.days_to_birthday()
    return f"No {name} in contacts"


@input_error
def no_command(*args):
    return " - not valid command entered\n" \
           " - type 'help' for commands"


@input_error
def hello() -> str:
    return "How can I help you?"


@input_error
def close() -> str:
    return "Good bye!"


commands = {
    "hello": hello,
    "hi": hello,
    "add": add,
    "+": add,
    "change": change,
    "find": find,
    "show_all": show_all,
    "show": show_all,
    "help": help,
    "bye": close,
    "close": close,
    "exit": close, 
    "birthday": set_birthday,
    "days_to_bd": days_to_birthday
}


@input_error
def parser(text: str) -> tuple[callable, tuple[str]]:
    text_lower = text.lower()
    words = text_lower.split()

    if words[0] in commands:
        command = commands[words[0]]
        args = tuple(words[1:])
        return command, args

    return no_command, ()


def main():
    while True:
        user_input = input(">>>")
        command, data = parser(user_input)

        if command == close:
            break

        result = command(*data)
        print(result)


if __name__ == "__main__":
    main()
