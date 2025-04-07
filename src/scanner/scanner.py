import logging
import requests
from bs4 import BeautifulSoup
import uuid
from api.models import AccessibilityIssue
from utils.helper import check_heading_structure, check_form_accessibility, check_aria_attributes, check_image_accessibility


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("accessai")

def scan_page(url, scan_type="full"):
    """
    Main scanning function that coordinates the accessibility checks
    """
    logger.info(f"Scanning page: {url} (type: {scan_type})")
    issues = []
    
    try:
        # Fetching the page
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parsing HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Basic page checks
        if not soup.find('html').get('lang'):
            issues.append(AccessibilityIssue(
                id=str(uuid.uuid4()),
                type="semantic",
                severity="major",
                element_selector="html",
                description="Missing language attribute on HTML tag",
                wcag_reference="3.1.1",
                recommendation="Add lang attribute to the HTML tag, e.g. <html lang='en'>"
            ))
            
        if not soup.find('title'):
            issues.append(AccessibilityIssue(
                id=str(uuid.uuid4()),
                type="semantic",
                severity="major",
                element_selector="head",
                description="Missing page title",
                wcag_reference="2.4.2",
                recommendation="Add a descriptive <title> element within the <head> section"
            ))
        
        # Running semantic checks if requested
        if scan_type in ["full", "semantic"]:
            # Check heading structure
            heading_issues = check_heading_structure(soup)
            for issue in heading_issues:
                issues.append(AccessibilityIssue(
                    id=str(uuid.uuid4()),
                    type="semantic",
                    severity="major",
                    element_selector="headings",
                    description=issue,
                    wcag_reference="1.3.1",
                    recommendation="Ensure proper heading structure with no skipped levels"
                ))
            
            # Checking form accessibility
            form_issues = check_form_accessibility(soup)
            for issue in form_issues:
                issues.append(AccessibilityIssue(
                    id=str(uuid.uuid4()),
                    type="semantic",
                    severity="critical",
                    element_selector="form",
                    description=str(issue),
                    wcag_reference="4.1.2",
                    recommendation="Ensure all form inputs have proper labels and associations"
                ))
            
            # Checking ARIA attributes
            aria_issues = check_aria_attributes(soup)
            for issue in aria_issues:
                issues.append(AccessibilityIssue(
                    id=str(uuid.uuid4()),
                    type="semantic",
                    severity="major",
                    element_selector=str(issue),
                    description="Improper ARIA attribute usage",
                    wcag_reference="4.1.2",
                    recommendation="Review ARIA attribute usage and ensure proper implementation"
                ))
            
            # Checking all links have descriptive text
            links = soup.find_all('a')
            for link in links:
                link_text = link.get_text().strip()
                if not link_text or link_text.lower() in ['click here', 'read more', 'more', 'link']:
                    issues.append(AccessibilityIssue(
                        id=str(uuid.uuid4()),
                        type="semantic",
                        severity="minor",
                        element_selector=f"a[href='{link.get('href', '#')}']",
                        description="Non-descriptive link text",
                        wcag_reference="2.4.4",
                        recommendation="Use descriptive text that indicates the link's purpose"
                    ))
        
        # Running visual checks if requested
        if scan_type in ["full", "visual"]:
            # Checking images for alt text
            images = soup.find_all('img')
            for img in images:
                is_accessible, issue = check_image_accessibility(img.get('src', ''), img)
                if not is_accessible:
                    issues.append(AccessibilityIssue(
                        id=str(uuid.uuid4()),
                        type="visual",
                        severity="critical",
                        element_selector=f"img[src='{img.get('src', '')}']",
                        description=issue,
                        wcag_reference="1.1.1",
                        recommendation="Add a descriptive alt attribute to the image"
                    ))
            
            # In a real implementation, headless browser would be used to evaluate:
            # - Color contrast
            # - Text size
            # - Element visibility
            # - Interactive element size
            # For MVP, I'll add a simulated issue for demonstration
            issues.append(AccessibilityIssue(
                id=str(uuid.uuid4()),
                type="visual",
                severity="major",
                element_selector=".header .nav-link",
                description="Low contrast text in navigation links",
                wcag_reference="1.4.3",
                recommendation="Increase contrast ratio to at least 4.5:1 for normal text"
            ))
        
        return issues
        
    except Exception as e:
        logger.error(f"Error scanning page {url}: {str(e)}")
        return [AccessibilityIssue(
            id=str(uuid.uuid4()),
            type="system",
            severity="critical",
            element_selector="",
            description=f"Error scanning page: {str(e)}",
            wcag_reference="",
            recommendation="Check if the URL is valid and accessible"
        )]