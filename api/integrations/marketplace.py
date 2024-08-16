import os

from dotenv import load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


from api.integrations.base import Integration
from api.interfaces import ListingResult
from api.logger import logger


class MarketplaceIntegration(Integration):
    def list(self, request) -> ListingResult:
        driver = self.getDriver(exec_name="selenium-fb:4444")
        try:
            wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)
            longWait = WebDriverWait(driver, 60)

            driver.get("https://www.facebook.com/marketplace")

            if not driver.find_elements(By.NAME, "email"):
                logger.debug("[FB] Already logged in to Facebook")
            else:
                if not (user := os.getenv("MARKETPLACE_USERNAME")) or not (
                    password := os.getenv("MARKETPLACE_PASSWORD")
                ):
                    logger.debug("[FB] Missing Facebook credentials")
                    raise Exception("Missing Facebook credentials")

                logger.debug("[FB] Logging in to Facebook")
                wait.until(lambda d: d.find_element(By.NAME, "email")).send_keys(user)
                wait.until(lambda d: d.find_element(By.NAME, "pass")).send_keys(
                    password, Keys.RETURN
                )

                longWait.until(
                    lambda d: d.find_element(
                        By.XPATH, '//span[text()="Create new listing"]'
                    )
                )

            logger.debug("[FB] Navigating to create listing page")
            driver.get("https://www.facebook.com/marketplace/create/item")

            # sometimes it doesn't redirect to the create listing page so we try again
            while (
                not driver.current_url
                == "https://www.facebook.com/marketplace/create/item"
            ):
                driver.get("https://www.facebook.com/marketplace/create/item")
                logger.debug("[FB] Retrying to navigate to create listing page")
                try:
                    wait.until(
                        lambda d: d.current_url
                        == "https://www.facebook.com/marketplace/create/item"
                    )
                except:
                    pass

            wait.until(
                lambda d: d.find_element(By.XPATH, '//label[@aria-label="Title"]')
            )

            logger.debug("[FB] Filling out listing form")
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

            ActionChains(driver).move_to_element(
                driver.find_element(By.XPATH, '//label[@aria-label="Category"]')
            ).click().perform()

            ActionChains(driver).move_to_element(
                wait.until(
                    lambda d: d.find_element(
                        By.XPATH, '//span[text()="Men\'s clothing & shoes"]'
                    )
                )
            ).click().perform()

            ActionChains(driver).move_to_element(
                driver.find_element(By.XPATH, '//label[@aria-label="Condition"]')
            ).click().perform()

            wait.until(
                lambda d: d.find_element(
                    By.XPATH,
                    f'//div[div/div/div/span[text()="{str(request.condition)}"]]',
                )
            ).click()

            driver.find_element(
                By.XPATH, '//label[@aria-label="Description"]/div/textarea'
            ).send_keys(request.description)

            wait.until(
                lambda d: d.find_element(By.XPATH, '//label[@aria-label="Size"]/input')
            ).send_keys(request.size)

            if request.tags:
                joinedTags = ",".join(request.tags.split("\n")) + ","
                driver.find_element(
                    By.XPATH, '//label[@aria-label="Product tags"]//textarea'
                ).send_keys(joinedTags)

            logger.debug("[FB] Publishing listing")
            driver.find_element(By.XPATH, '//div[@aria-label="Next"]').click()
            wait.until(
                lambda d: d.find_element(By.XPATH, '//div[@aria-label="Publish"]')
            ).click()

            logger.debug("[FB] Waiting for listing to be published")

            longWait.until(
                lambda d: d.current_url
                == "https://www.facebook.com/marketplace/you/selling"
            )

            logger.debug("[FB] Successfully listed on Marketplace")

            return ListingResult(
                url="https://www.facebook.com/marketplace/you/selling", success=True
            )
        except Exception as e:
            logger.debug("[FB] Failed to list on Marketplace: ", exc_info=e)
            return ListingResult(url="", success=False)
        finally:
            driver.quit()
