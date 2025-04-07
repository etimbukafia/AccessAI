from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class ScanRequest(BaseModel):
    url: HttpUrl
    scan_type: str = "full"  # Options: "full", "visual", "semantic"
    callback_url: Optional[HttpUrl] = None

class AccessibilityIssue(BaseModel):
    id: str
    type: str  # visual, semantic, etc.
    severity: str  # critical, major, minor
    element_selector: str
    description: str
    wcag_reference: str
    recommendation: str
    screenshot_data: Optional[str] = None

class ScanResult(BaseModel):
    scan_id: str
    url: HttpUrl
    status: str  # queued, in_progress, completed, failed
    issues: List[AccessibilityIssue] = []
    scan_type: str
    timestamp: datetime
    completion_time: Optional[datetime] = None
    summary: Optional[Dict[str, Any]] = None