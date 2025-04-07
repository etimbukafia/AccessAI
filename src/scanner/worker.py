from utils.helper import return_scan_results_and_queue, generate_summary
from scanner.scanner import scan_page
from datetime import datetime
import requests
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("accessai")

def worker():
    """
    Background worker that processes the scan queue
    """
    while True:
        try:
            scan_results, scan_queue = return_scan_results_and_queue()
            scan_id, url, scan_type, callback_url = scan_queue.get()
            
            # Update status to in_progress
            scan_results[scan_id].status = "in_progress"
            
            # Perform the scan
            issues = scan_page(url, scan_type)
            
            # Update the scan result
            scan_results[scan_id].issues = issues
            scan_results[scan_id].status = "completed"
            scan_results[scan_id].completion_time = datetime.now()
            scan_results[scan_id].summary = generate_summary(issues)
            
            # Send callback if provided
            if callback_url:
                try:
                    requests.post(
                        str(callback_url),
                        json=scan_results[scan_id].dict(),
                        headers={"Content-Type": "application/json"}
                    )
                except Exception as e:
                    logger.error(f"Failed to send callback: {str(e)}")
            
            logger.info(f"Scan completed: {scan_id}")
            
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            if scan_id in scan_results:
                scan_results[scan_id].status = "failed"
        
        finally:
            scan_queue.task_done()

# Start the worker thread
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()