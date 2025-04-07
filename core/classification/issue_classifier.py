class IssueClassifier:
    """Classifies accessibility issues by severity and impact"""
    
    def __init__(self, model_path=None):
        """Initialize the issue classifier with a pre-trained model"""
        # using a rule-based approach
        
        # Defining issue severity rules
        self.severity_rules = {
            # Critical issues (prevent use by certain users)
            "critical": [
                "missing alt text", 
                "keyboard trap",
                "empty form label",
                "empty button",
                "very low contrast",
                "missing page title"
            ],
            
            # Major issues (significant barriers)
            "major": [
                "low contrast",
                "missing heading structure",
                "missing form labels",
                "missing ARIA attributes",
                "small touch target"
            ],
            
            # Minor issues (nuisances but not barriers)
            "minor": [
                "redundant alt text",
                "minor contrast issues",
                "improper heading levels",
                "decorative images with alt text"
            ]
        }
    
    def _match_severity_pattern(self, issue_text):
        """Matching issue text against severity patterns"""
        issue_lower = issue_text.lower()
        
        for severity, patterns in self.severity_rules.items():
            for pattern in patterns:
                if pattern in issue_lower:
                    return severity
        
        # Default to "major" if no pattern matches
        return "major"
    
    def classify_issue(self, issue_data):
        """
        Classify an accessibility issue by severity and impact
        issue_data should include at least a description field
        """
        if not issue_data or "description" not in issue_data:
            return {"severity": "unknown", "confidence": 0}
            
        description = issue_data["description"]
        
        # Getting severity from rules
        severity = self._match_severity_pattern(description)
        
        # In a full implementation, this would use the ML model to classify
        # and would return a confidence score
        
        # For MVP, assigning confidence based on exactness of match
        confidence = 0.95 if any(pattern in description.lower() for pattern in self.severity_rules[severity]) else 0.7
        
        return {
            "severity": severity,
            "confidence": confidence,
            "wcag_level": "A" if severity == "critical" else "AA" if severity == "major" else "AAA"
        }