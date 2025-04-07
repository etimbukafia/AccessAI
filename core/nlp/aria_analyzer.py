class ARIAAnalyzer:
    """Analyzes ARIA attributes for proper usage"""
    
    def __init__(self):
        """Initialize the ARIA analyzer"""
        # Defining valid ARIA roles
        self.valid_roles = {
            "alert", "alertdialog", "application", "article", "banner", "button", 
            "cell", "checkbox", "columnheader", "combobox", "complementary", 
            "contentinfo", "definition", "dialog", "directory", "document", 
            "feed", "figure", "form", "grid", "gridcell", "group", "heading", 
            "img", "link", "list", "listbox", "listitem", "log", "main", 
            "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", 
            "menuitemradio", "navigation", "none", "note", "option", "presentation", 
            "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", 
            "rowheader", "scrollbar", "search", "searchbox", "separator", 
            "slider", "spinbutton", "status", "switch", "tab", "table", 
            "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", 
            "tooltip", "tree", "treegrid", "treeitem"
        }
        
        # Defining required ARIA attributes for specific roles
        self.required_attributes = {
            "slider": ["aria-valuemin", "aria-valuemax", "aria-valuenow"],
            "progressbar": ["aria-valuemin", "aria-valuemax", "aria-valuenow"],
            "checkbox": ["aria-checked"],
            "radio": ["aria-checked"],
            "combobox": ["aria-expanded"],
            "textbox": ["aria-multiline"],
        }
    
    def analyze_aria_usage(self, element_info):
        """
        Analyze ARIA attributes on an element for proper usage
        element_info: dict with keys 'tag', 'attributes', etc.
        """
        issues = []
        recommendations = []
        
        # Extracting element data
        tag = element_info.get("tag", "")
        attrs = element_info.get("attributes", {})
        
        # Getting role and ARIA attributes
        role = attrs.get("role", "")
        aria_attrs = {k: v for k, v in attrs.items() if k.startswith("aria-")}
        
        # Checking if role is valid
        if role and role not in self.valid_roles:
            issues.append(f"Invalid ARIA role: '{role}'")
            recommendations.append(f"Use a valid ARIA role instead of '{role}'")
        
        # Checking for required attributes based on role
        if role in self.required_attributes:
            missing = [attr for attr in self.required_attributes[role] if attr not in aria_attrs]
            if missing:
                issues.append(f"Missing required ARIA attributes for role '{role}': {', '.join(missing)}")
                recommendations.append(f"Add {', '.join(missing)} to element with role '{role}'")
        
        # Checking for redundant role
        if (tag == "button" and role == "button") or \
           (tag == "a" and role == "link") or \
           (tag == "input" and attrs.get("type") == "checkbox" and role == "checkbox"):
            issues.append(f"Redundant role '{role}' on <{tag}> element")
            recommendations.append(f"Remove redundant role '{role}' from <{tag}> element")
        
        # Checking aria-hidden on focusable elements
        if aria_attrs.get("aria-hidden") == "true" and \
           (tag in ["a", "button", "input", "select", "textarea"] or attrs.get("tabindex", "-1") != "-1"):
            issues.append("aria-hidden='true' used on a focusable element")
            recommendations.append("Remove aria-hidden='true' from focusable elements or make them non-focusable")
        
        # Checking for proper aria-label usage
        if "aria-label" in aria_attrs and not aria_attrs["aria-label"].strip():
            issues.append("Empty aria-label attribute")
            recommendations.append("Add descriptive text to aria-label or remove it")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "recommendations": recommendations
        }