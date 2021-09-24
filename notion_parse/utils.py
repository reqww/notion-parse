import os
import uuid
from collections import defaultdict
from dataclasses import dataclass

import emoji
import pdfkit
import urllib3
from urllib3.exceptions import LocationParseError, MaxRetryError
from urllib3.response import HTTPResponse

from .service import Template


@dataclass
class File(object):
    """ Пдфник """

    __response: HTTPResponse
    __template: Template
    __filepath: str

    save_dir = os.getcwd() + "/media"

    def get_pdf(self) -> str:
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
        pdfkit.from_file(self.__filepath, "media/out.pdf")
        # return str()


class TemplateChooser:
    """ Позволяет выбирать шаблон """

    @classmethod
    def __create_template(cls) -> Template:
        params = [
            input(getattr(Template, param))
            for param in filter(
                lambda x: not isinstance(getattr(Template, x), int)
                and x.startswith(f"_{Template.__name__}"),
                dir(Template),
            )
        ]
        template = Template(*params)
        template.dump()
        return template

    @classmethod
    def __switch(cls) -> bool:
        return input("Хочешь создать новый шаблон? [y/n] ") == "y"

    @classmethod
    def get_template(cls) -> Template:
        if Template.db.count:
            Template.db.get_all()
            if not cls.__switch():
                uid = int(input("Выбери id существующего шаблона: "))
                if template := Template.db.get_by_id(uid):
                    print(f"Используем шаблон: {template}")
                    return template
                else:
                    print("Такого шаблона нет...")

        print("Создаем новый шаблон.")
        return cls.__create_template()


status_dict = defaultdict(lambda: emoji.emojize("NOT OK :cross_mark:", language="en"))
status_dict[200] = emoji.emojize("OK :check_mark_button:", language="en")


@dataclass
class Downloader(object):
    """ Осуществялет скачивание страницы """

    __url: str

    _STATUS_CODE_DICT = status_dict
    tmp_path = os.getcwd() + "/tmp/"
    tmp_dir = "/tmp/"

    def _get_status_response(self, status) -> str:
        return self._STATUS_CODE_DICT[status]

    def download(self) -> None:
        http = urllib3.PoolManager()
        try:
            r = http.request("GET", self.__url, preload_content=False)
        except (MaxRetryError, LocationParseError):
            print("Что-то не так с твоей ссылкой...")
        else:
            print(f"Status code = {r.status} {self._get_status_response(r.status)} ")
            if r.status == 200:
                print(f"Your path: {self.__save_file(r)}.")
            else:
                print("Aborting...")
            r.release_conn()

    def __get_file_path(self, name) -> str:
        return self.tmp_path + name

    def __get_relative_path(self, name) -> str:
        return self.tmp_path + name

    @staticmethod
    def __get_tmp_file_name() -> str:
        return str(uuid.uuid4()) + ".html"

    def __write_to_file(self, response) -> str:
        name = self.__get_tmp_file_name()
        with open(self.__get_file_path(name), "wb") as tmp:
            while line := response.readline():
                print(line)
                tmp.write(line)

        return self.__get_relative_path(name)

    def __make_tmp(self, response) -> str:
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        return self.__write_to_file(response)

    def __save_file(self, response):
        self.filename = self.__make_tmp(response)
        return self.__save(response)

    def __save(self, response) -> str:
        try:
            template = TemplateChooser.get_template()
            file = File(response, template, self.filename)
        except BaseException:
            print("Something went wrong...")
            raise
        else:
            return file.get_pdf()
        finally:
            # os.remove(self.filename)
            pass
