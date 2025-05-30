from fastapi import BackgroundTasks
from models import ScanRequest, ScanResult
from datetime import datetime
import uuid
from utils.helper import return_scan_results_and_queue
from fastapi import HTTPException, FastAPI
from typing import List
from scanner.worker import scan_queue, scan_results

app = FastAPI(title="AccessAI API", description="AI Accessibility Insight Agent")


@app.post("/scan", response_model=ScanResult)
async def create_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to start a new accessibility scan
    """
    scan_id = str(uuid.uuid4())
    
    # Creating a new scan result
    scan_result = ScanResult(
        scan_id=scan_id,
        url=scan_request.url,
        status="queued",
        scan_type=scan_request.scan_type,
        timestamp=datetime.now(),
        issues=[]
    )

    # Storing in in-memory database
    scan_results[scan_id] = scan_result
    
    # Adding to processing queue
    scan_queue.put((scan_id, scan_request.url, scan_request.scan_type, scan_request.callback_url))
    
    return scan_result

@app.get("/scan/{scan_id}", response_model=ScanResult)
async def get_scan_result(scan_id: str):
    """
    Endpoint to retrieve scan results
    """
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_results[scan_id]

@app.get("/scans", response_model=List[ScanResult])
async def list_scans():
    """
    Endpoint to list all scans
    """
    return list(scan_results.values())

@app.delete("/scan/{scan_id}")
async def delete_scan(scan_id: str):
    """
    Endpoint to delete a scan
    """
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    del scan_results[scan_id]
    return {"status": "deleted"}