import sys
from pathlib import Path
import glob
import shutil
import os
import subprocess
import time

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from modules.meta_requester import MetaAccountRequester
from utils.logger import setup_logger
from config import loader

def cleanup_chrome():
    """Clean up Chrome processes and temporary files"""
    # Kill Chrome processes more aggressively
    commands = [
        ['pkill', '-f', 'chrome'],
        ['pkill', '-f', 'chromium'],
        ['pkill', '-f', 'chromedriver']
    ]
    
    for cmd in commands:
        subprocess.run(cmd, stderr=subprocess.DEVNULL)
    time.sleep(2)  # Give processes time to fully terminate
    
    # Clean up temporary directories
    patterns = [
        "/tmp/.org.chromium.*",
        "/tmp/.com.google.*",
        "/tmp/chrome_*",
        os.path.expanduser("~/.cache/google-chrome"),
        os.path.expanduser("~/.config/google-chrome"),
        os.path.expanduser("~/.chrome_debug_profile")
    ]
    
    for pattern in patterns:
        try:
            paths = glob.glob(pattern)
            for path in paths:
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Failed to remove {path}: {e}")
        except Exception as e:
            logger.warning(f"Error processing pattern {pattern}: {e}")

if __name__ == "__main__":
    logger = setup_logger("meta_cron_bot")
    
    try:
        # Ensure thorough cleanup before starting
        cleanup_chrome()        
        # Add delay to ensure system resources are freed
        time.sleep(2)
        requester = MetaAccountRequester(headless=loader.HEADLESS, timeout=30)
        requester.login()
        requester.submit_data_request()
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        
    finally:
        logger.info("Cleaning up and closing the requester")
        if 'requester' in locals():
            requester.close()
        cleanup_chrome()
