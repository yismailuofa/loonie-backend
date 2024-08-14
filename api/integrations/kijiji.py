import os

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from api.integrations.base import Integration
from api.interfaces import ListingResult
from api.logger import logger

load_dotenv()


class KijijiIntegration(Integration):
    def list(self, request) -> ListingResult:
        driver = self.getDriver()
        try:
            wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

            driver.get("https://www.kijiji.ca/p-select-category.html")

            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "username")),
                    EC.presence_of_element_located((By.NAME, "AdTitleForm")),
                )
            )

            if not driver.find_elements(By.ID, "username"):
                logger.debug("Already logged in to Kijiji")
            else:
                if not (user := os.getenv("KIJIJI_USERNAME")) or not (
                    password := os.getenv("KIJIJI_PASSWORD")
                ):
                    logger.debug("Missing Facebook credentials")
                    raise Exception("Missing Facebook credentials")

                logger.debug("Logging in to Kijiji")
                wait.until(lambda d: d.find_element(By.ID, "username")).send_keys(user)
                wait.until(lambda d: d.find_element(By.ID, "password")).send_keys(
                    password, Keys.RETURN
                )

            logger.debug("Adding title")
            wait.until(lambda d: d.find_element(By.NAME, "AdTitleForm")).send_keys(
                request.title, Keys.RETURN
            )

            logger.debug("Selecting category")
            wait.until(
                lambda d: d.find_element(By.XPATH, '//span[text()="Buy & Sell"]')
            ).click()
            wait.until(
                lambda d: d.find_element(By.XPATH, '//span[text()="Clothing"]')
            ).click()
            wait.until(
                lambda d: d.find_element(By.XPATH, '//span[text()="Men\'s Shoes"]')
            ).click()

            wait.until(
                lambda d: d.current_url.startswith(
                    "https://www.kijiji.ca/p-post-ad.html"
                )
            )

            wait.until(
                lambda d: d.find_element(By.XPATH, '//label[text()="Men\'s Shoes"]')
            ).click()

            wait.u

            return ListingResult(
                url="https://www.kijiji.ca/p-select-category.html", success=True
            )

        except Exception as e:
            logger.debug("Failed to list on Kijiji: ", exc_info=e)
            return ListingResult(url="", success=False)
        finally:
            driver.quit()
