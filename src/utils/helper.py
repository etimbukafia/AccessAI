# Accessiblity standards

def return_wcag_guidelines():
    WCAG_GUIDELINES = {
        "1.1.1": "Non-text Content: Provide text alternatives for non-text content",
        "1.4.3": "Contrast: Text has sufficient contrast against background",
        "1.4.4": "Resize text: Text can be resized without loss of content",
        "2.1.1": "Keyboard: All functionality is available from a keyboard",
        "2.4.2": "Page Titled: Pages have titles that describe topic or purpose",
        "2.4.4": "Link Purpose: Purpose of each link can be determined from link text",
        "3.1.1": "Language of Page: Human language of page is programmatically determinable",
        "4.1.1": "Parsing: Markup is used according to specification",
        "4.1.2": "Name, Role, Value: All UI components have accessible names and roles",
    }

# Visual accessibility checks
def check_color_contrast(element_style):
    """
    Simple check for color contrast issues based on element style
    In a real implementation, this would use a proper color contrast algorithm
    """
    # Mock implementation
    foreground = element_style.get('color', '#000000')
    background = element_style.get('background-color', '#FFFFFF')
    
    # Simplified contrast check - would be more sophisticated later
    if foreground == background:
        return False, "No contrast between foreground and background"
    return True, None

def check_image_accessibility(img_url, img_element):
    """
    Check if an image has appropriate alt text
    """
    alt_text = img_element.get('alt', '')
    if not alt_text:
        return False, "Missing alt text for image"
    elif alt_text.lower() in ['image', 'photo', 'picture', 'img', '']:
        return False, "Generic or empty alt text"
    return True, None

def check_text_size(element_style):
    """
    Check if text size is accessible
    """
    font_size = element_style.get('font-size', '16px')
    try:
        size = int(font_size.replace('px', ''))
        if size < 12:
            return False, "Text size too small for readability"
    except:
        pass
    return True, None

# Semantic accessibility checks
def check_heading_structure(soup):
    """
    Check if heading structure is appropriate
    """
    issues = []
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not soup.find('h1'):
        issues.append("Page missing main heading (h1)")
    
    # Checking for skipped heading levels
    heading_levels = [int(h.name[1]) for h in headings]
    for i in range(1, len(heading_levels)):
        if heading_levels[i] > heading_levels[i-1] + 1:
            issues.append(f"Skipped heading level from h{heading_levels[i-1]} to h{heading_levels[i]}")
    
    return issues

def check_form_accessibility(soup):
    """
    Check if forms are properly labeled and accessible
    """
    issues = []
    forms = soup.find_all('form')
    
    for form in forms:
        inputs = form.find_all(['input', 'select', 'textarea'])
        for input_elem in inputs:
            # Skip hidden inputs
            if input_elem.get('type') == 'hidden':
                continue
                
            input_id = input_elem.get('id')
            if not input_id:
                issues.append(f"Form input missing ID attribute: {input_elem}")
                continue
                
            # Checking for associated label
            label = form.find('label', attrs={'for': input_id})
            if not label:
                issues.append(f"Form input missing associated label: {input_elem}")
    
    return issues

def check_aria_attributes(soup):
    """
    Check for proper ARIA attribute usage
    """
    issues = []
    elements_with_aria = soup.find_all(lambda tag: any(attr.startswith('aria-') for attr in tag.attrs))
    
    for element in elements_with_aria:
        # Checking for aria-label without aria-role
        if element.has_attr('aria-label') and not element.has_attr('role'):
            issues.append(f"Element has aria-label but no role: {element}")
        
        # Checking for invalid aria-hidden values
        if element.has_attr('aria-hidden') and element['aria-hidden'] not in ['true', 'false']:
            issues.append(f"Invalid aria-hidden value: {element}")
    
    return issues

def generate_summary(issues):
    """
    Generate a summary of accessibility issues
    """
    severity_counts = {"critical": 0, "major": 0, "minor": 0}
    type_counts = {"visual": 0, "semantic": 0, "system": 0}
    
    for issue in issues:
        severity_counts[issue.severity] += 1
        type_counts[issue.type] += 1
    
    overall_score = 100
    # Deduct points based on severity
    overall_score -= severity_counts["critical"] * 10
    overall_score -= severity_counts["major"] * 5
    overall_score -= severity_counts["minor"] * 1
    
    # Ensure score stays within 0-100 range
    overall_score = max(0, min(100, overall_score))
    
    # Generate top recommendations (in a real app, this would be more sophisticated)
    top_recommendations = []
    critical_issues = [issue for issue in issues if issue.severity == "critical"]
    for issue in critical_issues[:3]:  # Get top 3 critical issues
        top_recommendations.append(issue.recommendation)
    
    return {
        "total_issues": len(issues),
        "severity_counts": severity_counts,
        "type_counts": type_counts,
        "overall_score": overall_score,
        "top_recommendations": top_recommendations
    }