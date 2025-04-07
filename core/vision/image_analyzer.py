import os
import cv2
import numpy as np
import logging
import re

logger = logging.getLogger("accessai.vision.image")

class ImageAnalyzer:
    """Uses computer vision to analyze images for accessibility issues"""
    
    def __init__(self, model_path=None):
        """
        Initialize the image analyzer with a pre-trained image classification model
        """
        self.model_path = model_path
        self.model = None
        if model_path and os.path.exists(model_path):
            logger.info(f"Loading image analysis model from {model_path}")
        else:
            logger.warning("No image analysis model provided, using rule-based analysis only")
    
    def analyze_decorative_vs_informative(self, image):
        """
        Determine if an image is likely decorative or informative
        This would use a trained classifier in a full implementation
        """
        
        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate image statistics
        avg_intensity = np.mean(gray)
        std_intensity = np.std(gray)
        
        # Simple edge detection to measure complexity
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Heuristic: If image has high edge density and variance, it's likely informative
        is_informative = edge_density > 0.05 and std_intensity > 40
        
        confidence = min(0.95, max(0.6, edge_density * 5 + std_intensity / 100))
        
        return {
            "is_informative": is_informative,
            "confidence": round(confidence, 2),
            "edge_density": round(edge_density, 3),
            "recommendation": "Add descriptive alt text" if is_informative else "Consider marking as decorative"
        }
    
    def analyze_alt_text_quality(self, image, alt_text):
        """
        Analyze the quality of alt text for an image
        Returns a quality score and recommendation
        """
        
        word_count = len(alt_text.split())
        
        quality_score = 0.5  # Default medium score
        
        # Check for common low-quality patterns
        if word_count < 2:
            quality_score = 0.2
            recommendation = "Alt text is too short. Add more descriptive content."
        elif re.search(r'image|picture|photo|graphic|icon', alt_text, re.IGNORECASE):
            quality_score = 0.3
            recommendation = "Alt text contains redundant terms like 'image' or 'photo'."
        elif word_count > 20:
            quality_score = 0.7
            recommendation = "Alt text is comprehensive but consider being more concise."
        else:
            quality_score = 0.8
            recommendation = "Alt text appears adequate."
        
        return {
            "quality_score": quality_score,
            "word_count": word_count,
            "recommendation": recommendation
        }