import logging

logger = logging.getLogger("accessai.vision.touch_target")

class TouchTargetAnalyzer:
    """Analyzes interactive elements for appropriate touch target size"""
    
    def __init__(self):
        """Initialize the touch target analyzer with required constants"""
        # WCAG 2.5.5 recommends at least 44x44 CSS pixels
        self.MIN_TARGET_SIZE = 44
    
    def analyze_touch_target(self, element_image, element_type="button"):
        """
        Analyze if an interactive element meets touch target size requirements
        """
        height, width = element_image.shape[:2]
        
        meets_standard = width >= self.MIN_TARGET_SIZE and height >= self.MIN_TARGET_SIZE
        
        result = {
            "width_px": width,
            "height_px": height,
            "meets_standards": meets_standard,
            "element_type": element_type
        }
        
        if not meets_standard:
            result["recommendation"] = f"Increase the size of this {element_type} to at least {self.MIN_TARGET_SIZE}x{self.MIN_TARGET_SIZE} pixels"
            
            # Adding more specific recommendations
            if width < self.MIN_TARGET_SIZE and height < self.MIN_TARGET_SIZE:
                result["recommendation"] += " in both width and height"
            elif width < self.MIN_TARGET_SIZE:
                result["recommendation"] += " in width"
            else:
                result["recommendation"] += " in height"
        
        return result