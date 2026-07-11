import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log file name with current date
LOG_FILE = os.path.join(
    LOG_DIR,
    f"calcsync_{datetime.now().strftime('%Y-%m-%d')}.log"
)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    format="[ %(asctime)s ] %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    encoding="utf-8"
)

logger = logging.getLogger("CalSync")