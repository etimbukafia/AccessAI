import cv2
import numpy as np
import logging

logger = logging.getLogger("accessai.vision.text_size")

class TextSizeAnalyzer:
    """Analyzes text size for readability"""
    
    def __init__(self):
        """Initialize the text size analyzer"""
        self.MIN_TEXT_SIZE_PX = 16  # Minimum recommended text size in pixels
    
    def estimate_text_size(self, text_element_image):
        """
        Estimate the text size from an image of text
        Returns the estimated size in pixels
        """
        # Converting image to grayscale
        gray = cv2.cvtColor(text_element_image, cv2.COLOR_BGR2GRAY)
        
        # Applying thresholding to isolate text
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Finding contours which represent text components
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0
            
        # Calculating height statistics of contours
        heights = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out very small components (noise)
            if h > 2:
                heights.append(h)
        
        if not heights:
            return 0
            
        # Use median height as estimate of text size
        # This is more robust than mean for text with mixed case
        median_height = np.median(heights)
        
        return median_height
    
    def analyze_text_size(self, text_element_image):
        """
        Analyze if text size meets accessibility standards
        Returns size estimation and recommendation
        """
        estimated_size = self.estimate_text_size(text_element_image)
        
        result = {
            "estimated_size_px": round(estimated_size, 1),
            "meets_standards": estimated_size >= self.MIN_TEXT_SIZE_PX
        }
        
        if not result["meets_standards"]:
            result["recommendation"] = f"Increase text size to at least {self.MIN_TEXT_SIZE_PX}px for better readability"
        
        return result