import io
import numpy as np
import logging
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

logger = logging.getLogger("accessai.browser.screenshot")

class ScreenshotProcessor:
    """Takes screenshots of web pages and processes them for analysis"""
    
    def __init__(self):
        """Initialize the screenshot processor with a headless browser"""
        # Setting up headless Chrome
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("Screenshot processor initialized with headless Chrome")
        except Exception as e:
            logger.error(f"Failed to initialize headless Chrome: {str(e)}")
            self.driver = None
    
    def take_screenshot(self, url):
        """Take a screenshot of a web page"""
        if not self.driver:
            logger.error("Headless browser not available")
            return None
            
        try:
            self.driver.get(url)
            # Waiting for page to load
            time.sleep(2)
            
            # Taking screenshot
            screenshot = self.driver.get_screenshot_as_png()
            
            # Converting to numpy array
            image = np.array(Image.open(io.BytesIO(screenshot)))
            return image
        except Exception as e:
            logger.error(f"Failed to take screenshot of {url}: {str(e)}")
            return None
    
    def get_element_screenshot(self, element_selector):
        """Get a screenshot of a specific element"""
        if not self.driver:
            logger.error("Headless browser not available")
            return None
            
        try:
            element = self.driver.find_element_by_css_selector(element_selector)
            
            # Getting element location and size
            location = element.location
            size = element.size
            
            # Taking screenshot
            screenshot = self.driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot))
            
            # Cropping to element
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            
            image = image.crop((left, top, right, bottom))
            
            return np.array(image)
        except Exception as e:
            logger.error(f"Failed to get element screenshot: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()