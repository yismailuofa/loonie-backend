from abc import ABC, abstractmethod

from selenium import webdriver

from api.interfaces import ListingRequest, ListingResult


class Integration(ABC):
    def __init__(self):
        self.DEFAULT_TIMEOUT = 10

    @abstractmethod
    def list(self, request: ListingRequest) -> ListingResult:
        raise NotImplementedError

    def getDriver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("user-data-dir=selenium")
        # options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)

        return driver
