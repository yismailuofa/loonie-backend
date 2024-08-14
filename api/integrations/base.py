from abc import ABC, abstractmethod

from api.interfaces import ListingRequest, ListingResult
from selenium import webdriver


class Integration(ABC):
    def __init__(self):
        self.DEFAULT_TIMEOUT = 10

    @abstractmethod
    def list(self, request: ListingRequest) -> ListingResult:
        raise NotImplementedError

    def getDriver(self) -> webdriver.Chrome | webdriver.Remote:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--window-size=1920,1080")

        # options.add_argument("--user-data-dir=selenium")
        # driver = webdriver.Chrome(options=options)

        options.add_argument("--user-data-dir=/home/seluser/selenium")
        driver = webdriver.Remote(
            options=options, command_executor="http://selenium:4444/wd/hub"
        )

        return driver
