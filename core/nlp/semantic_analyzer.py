import re
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger("accessai.nlp.semantic")

class SemanticAnalyzer:
    """Analyzes text content for semantic accessibility issues"""
    
    def __init__(self):
        """Initialize the semantic analyzer with required models"""
        try:
            # Loading readability assessment model
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            # use fine-tuned model for readability scoring
            self.model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
            logger.info("Semantic analyzer initialized with DistilBERT model")
        except Exception as e:
            logger.error(f"Failed to load semantic analysis models: {str(e)}")
            self.tokenizer = None
            self.model = None
    
    def analyze_readability(self, text):
        """
        Analyze text readability
        Returns a readability score and improvement suggestions
        """
        if not text:
            return {
                "score": 0,
                "suggestions": ["No text provided for analysis"]
            }
        
        # using simple rule-based metric
        
        # Calculating average sentence length
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return {
                "score": 0,
                "suggestions": ["Text contains no complete sentences"]
            }
            
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Calculating average word length
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Simple readability score (lower is easier to read)
        # simplified version of metrics like Flesch-Kincaid
        readability_score = (0.39 * avg_sentence_length) + (11.8 * avg_word_length) - 15.59
        
        # Normalizing to 0-100 scale (100 is most readable)
        normalized_score = max(0, min(100, 100 - readability_score * 2))
        
        # Generating suggestions
        suggestions = []
        if avg_sentence_length > 20:
            suggestions.append("Consider using shorter sentences to improve readability")
        
        if avg_word_length > 5.5:
            suggestions.append("Use simpler, shorter words where possible")
        
        # Checking for passive voice (simplified check)
        passive_pattern = r'\b(am|is|are|was|were|be|being|been)\s+(\w+ed|written|done|made|said|known)\b'
        passive_count = len(re.findall(passive_pattern, text))
        if passive_count > len(sentences) * 0.3:
            suggestions.append("Reduce use of passive voice for clearer communication")
        
        return {
            "score": round(normalized_score, 1),
            "metrics": {
                "avg_sentence_length": round(avg_sentence_length, 1),
                "avg_word_length": round(avg_word_length, 1),
                "passive_voice_instances": passive_count
            },
            "suggestions": suggestions
        }
    
    def analyze_heading_hierarchy(self, headings):
        """
        Analyze the semantic structure of headings
        headings: list of (level, text) tuples, e.g. [(1, "Main Heading"), (2, "Subheading")]
        """
        if not headings:
            return {
                "is_valid": False,
                "issues": ["No headings found on the page"]
            }
        
        issues = []
        
        # Checking if starts with h1
        if headings[0][0] != 1:
            issues.append(f"Page does not start with an h1 heading (starts with h{headings[0][0]})")
        
        # Checking for skipped levels
        current_level = 1
        for i, (level, text) in enumerate(headings):
            if level > current_level + 1:
                issues.append(f"Heading level skipped from h{current_level} to h{level} at '{text}'")
            current_level = level
        
        # Checking for empty or very short headings
        for level, text in headings:
            if len(text.strip()) < 3:
                issues.append(f"Empty or very short h{level} heading found")
        
        # Checking for duplicate headings
        heading_texts = [text.lower().strip() for _, text in headings]
        duplicates = set([text for text in heading_texts if heading_texts.count(text) > 1])
        if duplicates:
            for dup in duplicates:
                issues.append(f"Duplicate heading text: '{dup}'")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "recommendation": "Ensure heading levels don't skip (e.g., from h1 to h3) and start with h1" if issues else ""
        }