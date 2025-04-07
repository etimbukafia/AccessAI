import numpy as np
import logging
from sklearn.cluster import KMeans

logger = logging.getLogger("accessai.vision.contrast")

class ContrastAnalyzer:
    """Analyzes color contrast between text and background"""
    
    def __init__(self):
        """Initializing the contrast analyzer with required constants"""
        # WCAG contrast ratios
        self.MIN_CONTRAST_NORMAL = 4.5  # For normal text
        self.MIN_CONTRAST_LARGE = 3.0   # For large text (>= 18pt or bold >= 14pt)
        self.MIN_CONTRAST_UI = 3.0      # For UI components
        
    def _rgb_to_luminance(self, color):
        """
        Converts RGB color to relative luminance
        """
        # Normalizing RGB values to 0-1
        r, g, b = [x/255 for x in color]
        
        # Converting sRGB values to linear RGB
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        # Calculating luminance using WCAG formula
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def calculate_contrast_ratio(self, color1, color2):
        """
        Calculates contrast ratio between two colors
        Formula: (L1 + 0.05) / (L2 + 0.05), where L1 is the lighter and L2 is the darker
        """
        # Calculating luminance values
        l1 = self._rgb_to_luminance(color1)
        l2 = self._rgb_to_luminance(color2)
        
        # Ensure l1 is the lighter color (higher luminance)
        if l1 < l2:
            l1, l2 = l2, l1
            
        # Calculating contrast ratio
        return (l1 + 0.05) / (l2 + 0.05)
    
    def extract_dominant_colors(self, image_data, n_colors=2):
        """
        Extracts dominant colors from an image region using K-means clustering
        """
        # Reshaping image for clustering
        pixels = np.float32(image_data.reshape(-1, 3))
        
        # Use K-means to find dominant colors
        kmeans = KMeans(n_clusters=n_colors, random_state=42)
        kmeans.fit(pixels)
        
        # Getting the colors and their proportions
        colors = kmeans.cluster_centers_.astype(int)
        counts = np.bincount(kmeans.labels_)
        
        # Sorting colors by frequency (most common first)
        colors_with_counts = sorted(zip(colors, counts), key=lambda x: x[1], reverse=True)
        return [color.tolist() for color, _ in colors_with_counts]
    
    def analyze_text_contrast(self, text_region, background_region):
        """
        Analyzes contrast between text and background regions
        Returns: contrast ratio, pass/fail status, and recommendation
        """
        # Extracting dominant colors from text and background
        text_colors = self.extract_dominant_colors(text_region)
        bg_colors = self.extract_dominant_colors(background_region)
        
        # Use the most dominant colors
        text_color = text_colors[0]
        bg_color = bg_colors[0]
        
        # Calculating contrast ratio
        ratio = self.calculate_contrast_ratio(text_color, bg_color)
        
        # Evaluating against WCAG standards
        passes_normal = ratio >= self.MIN_CONTRAST_NORMAL
        passes_large = ratio >= self.MIN_CONTRAST_LARGE
        
        result = {
            "contrast_ratio": round(ratio, 2),
            "passes_normal_text": passes_normal,
            "passes_large_text": passes_large,
            "text_color": text_color,
            "background_color": bg_color
        }
        
        # Generates recommendation if failing
        if not passes_normal:
            # Calculats required adjustment to meet standards
            # Try color theory later
            # suggests specific color changes
            if text_color[0] + text_color[1] + text_color[2] > bg_color[0] + bg_color[1] + bg_color[2]:
                # Text is lighter than background, make it even lighter
                recommendation = "Increase the lightness of the text or darken the background"
            else:
                # Text is darker than background, make it even darker
                recommendation = "Increase the darkness of the text or lighten the background"
                
            result["recommendation"] = recommendation
            
        return result