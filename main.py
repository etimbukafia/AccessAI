import uvicorn
import logging
from src.api.routes import app
from src.scanner.worker import start_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("accessai")

if __name__ == "__main__":
    # Start the background worker
    start_worker()
    
    # Start the API server
    logger.info("Starting AccessAI API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)