from .utils import Downloader


def main():
    downloader = Downloader(input("Введи ссылку: "))
    downloader.download()


if __name__ == "__main__":
    main()
