import pickle
from dataclasses import dataclass

from .settings import DATABASE_NAME


class PickleDatabase:
    def __init__(self):
        open(DATABASE_NAME, "ab")

    @staticmethod
    def save(instance):
        with open(DATABASE_NAME, "ab") as db:
            pickle.dump(instance, db, pickle.HIGHEST_PROTOCOL)

    @property
    def count(self) -> int:
        counter = 0
        with open(DATABASE_NAME, "rb") as db:
            try:
                while pickle.load(db):
                    counter += 1
            except EOFError:
                return counter

    def get_all(self) -> None:
        print("Существующие шаблоны:")
        with open(DATABASE_NAME, "rb") as db:
            i = 0
            while i < self.count:
                print(pickle.load(db))
                i += 1

    @staticmethod
    def get_by_id(uid: int) -> object:
        with open(DATABASE_NAME, "rb") as db:
            i = 0
            while i < uid - 1:
                try:
                    pickle.load(db)
                except EOFError:
                    return None
                i += 1

            return pickle.load(db)


@dataclass
class Template:
    __group: str = "Введи группу: "
    __name: str = "Введи имя: "
    __subject: str = "Введи предмет: "
    __uid: int = 0

    db = PickleDatabase()

    def __str__(self):
        return f"{self.__uid}: {self.__group}, {self.__name}, {self.__subject}"

    def dump(self) -> None:
        self.__uid = self.db.count + 1
        self.db.save(self)
