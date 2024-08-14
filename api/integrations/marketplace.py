import os

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


from api.integrations.base import Integration
from api.interfaces import ListingResult
from api.logger import logger


class MarketplaceIntegration(Integration):
    def list(self, request) -> ListingResult:
        try:
            driver = self.getDriver()
            wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

            driver.get("https://www.facebook.com/marketplace")

            if not driver.find_elements(By.NAME, "email"):
                logger.debug("Already logged in to Facebook")
            else:
                logger.debug("Waiting for Facebook login")
                wait.until(lambda d: d.find_element(By.NAME, "email"))
                wait.until(lambda d: d.find_element(By.NAME, "pass"))

                if not (user := os.getenv("MARKETPLACE_USERNAME")) or not (
                    password := os.getenv("MARKETPLACE_PASSWORD")
                ):
                    logger.debug("Missing Facebook credentials")
                    raise Exception("Missing Facebook credentials")

                logger.debug("Logging in to Facebook")
                driver.find_element(By.NAME, "email").send_keys(user)
                driver.find_element(By.NAME, "pass").send_keys(password)
                driver.find_element(By.NAME, "pass").send_keys(Keys.RETURN)

            logger.debug("Navigating to create listing page")
            driver.get("https://www.facebook.com/marketplace/create/item")
            wait.until(
                lambda d: d.find_element(By.XPATH, '//label[@aria-label="Title"]')
            )

            logger.debug("Filling out listing form")
            if request.images:
                imageInput = driver.find_element(
                    By.XPATH, "//input[@accept='image/*,image/heif,image/heic']"
                )
                joinedPaths = "\n".join(request.images)
                imageInput.send_keys(joinedPaths)

            driver.find_element(
                By.XPATH, '//label[@aria-label="Title"]/input'
            ).send_keys(request.title)

            driver.find_element(
                By.XPATH, '//label[@aria-label="Price"]/input'
            ).send_keys(request.price)

            driver.find_element(By.XPATH, '//label[@aria-label="Category"]').click()
            driver.find_element(
                By.XPATH, '//span[text()="Men\'s clothing & shoes"]'
            ).click()

            driver.find_element(By.XPATH, '//label[@aria-label="Condition"]').click()
            driver.find_element(
                By.XPATH, f'//span[text()="{str(request.condition)}"]'
            ).click()

            driver.find_element(
                By.XPATH, '//label[@aria-label="Description"]/div/textarea'
            ).send_keys(request.description)

            wait.until(
                lambda d: d.find_element(By.XPATH, '//label[@aria-label="Size"]/input')
            )
            driver.find_element(
                By.XPATH, '//label[@aria-label="Size"]/input'
            ).send_keys(request.size)

            if request.tags:
                joinedTags = ", ".join(request.tags.split("\n")) + ","
                driver.find_element(
                    By.XPATH, '//label[@aria-label="Product tags"]//textarea'
                ).send_keys(joinedTags)

            logger.debug("Publishing listing")
            driver.find_element(By.XPATH, '//div[@aria-label="Next"]').click()
            driver.find_element(By.XPATH, '//div[@aria-label="Publish"]').click()

            logger.debug("Waiting for listing to be published")
            longWait = WebDriverWait(driver, 30)
            longWait.until(
                lambda d: d.current_url
                == "https://www.facebook.com/marketplace/you/selling"
            )

            wait.until(
                lambda d: d.find_element(By.XPATH, f"//span[text()='{request.title}']")
            )
            driver.find_element(By.XPATH, f"//span[text()='{request.title}']").click()

            wait.until(
                lambda d: d.find_element(
                    By.XPATH, '//div[@aria-label="Your Listing"]//a'
                )
            )
            url = driver.find_element(
                By.XPATH, '//div[@aria-label="Your Listing"]//a'
            ).get_attribute("href")

            if not url:
                logger.debug("Failed to get listing URL")
                raise Exception("Failed to get listing URL")

            return ListingResult(url=url, success=True)
        except Exception as e:
            logger.debug("Failed to list on Marketplace: %s", exc_info=e)
            return ListingResult(url="", success=False)
