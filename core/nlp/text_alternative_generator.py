import torch
import logging
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger("accessai.nlp.text_alt")

class TextAlternativeGenerator:
    """Generates and evaluates text alternatives for non-text content"""
    
    def __init__(self, model_path=None):
        """Initialize with pre-trained models"""
        try:
            # Loading models
            self.tokenizer = AutoTokenizer.from_pretrained("t5-base")
            self.model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
            logger.info("Text alternative generator initialized with T5 model")
        except Exception as e:
            logger.error(f"Failed to load text alternative models: {str(e)}")
            self.tokenizer = None
            self.model = None
    
    def generate_alt_text(self, image_description):
        """
        Generate alternative text based on image description
        In a full implementation, this would use a multimodal model that takes the image directly
        """
        if not self.tokenizer or not self.model:
            return "Unable to generate alternative text"
            
        try:
            # using a text-to-text approach
            prompt = f"Generate accessible alt text for an image described as: {image_description}"
            
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            # Generating alt text
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=50,
                    num_beams=4,
                    early_stopping=True
                )
                
            alt_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Removing common prefixes in generated text
            alt_text = re.sub(r'^(Alt text:|Alternative text:|Image shows|Image of|Image description:)\s*', '', alt_text)
            
            return alt_text
        except Exception as e:
            logger.error(f"Failed to generate alt text: {str(e)}")
            return "Error generating alternative text"
    
    def evaluate_alt_text(self, alt_text):
        """
        Evaluate the quality of alternative text
        Returns a score and improvement suggestions
        """
        # Simple rule-based evaluation
        score = 1.0  # Starting with perfect score
        suggestions = []
        
        # Checking length
        if len(alt_text) < 10:
            score -= 0.3
            suggestions.append("Alt text is too short. Add more descriptive details.")
        elif len(alt_text) > 125:
            score -= 0.1
            suggestions.append("Alt text is quite long. Consider being more concise.")
        
        # Checking for redundant phrases
        redundant_phrases = ["image of", "picture of", "photo of", "graphic of"]
        for phrase in redundant_phrases:
            if phrase in alt_text.lower():
                score -= 0.2
                suggestions.append(f"Remove redundant phrase '{phrase}' from alt text.")
                break
        
        # Checking for lack of specificity
        generic_terms = ["item", "thing", "object", "stuff"]
        for term in generic_terms:
            if re.search(rf'\b{term}\b', alt_text.lower()):
                score -= 0.1
                suggestions.append(f"Replace generic term '{term}' with more specific description.")
        
        # Ensure score is between 0 and 1
        score = max(0, min(1, score))
        
        return {
            "score": round(score, 2),
            "suggestions": suggestions
        }