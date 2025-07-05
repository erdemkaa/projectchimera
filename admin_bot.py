# project_chimera/admin_bot.py

import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for the bot
# In a real scenario, this would be more robust (e.g., reading from config, handling sessions)
# For CTF, we assume the Flask app is running on localhost:5000
FLASK_APP_URL = "http://localhost:5000"
OVERSEER_PROFILE_ID = 1 # Assuming 'overseer' user has ID 1
REVIEW_INTERVAL_SECONDS = 10 # How often the bot reviews the profile

def run_admin_bot():
    logger.info(f"Admin review bot started. Reviewing profile {OVERSEER_PROFILE_ID} every {REVIEW_INTERVAL_SECONDS} seconds.")
    while True:
        try:
            # Simulate Dr. Albright (or an admin process) reviewing the Overseer's profile
            # This will hit the /admin_review_profile/<user_id> endpoint
            review_url = f"{FLASK_APP_URL}/admin_review_profile/{OVERSEER_PROFILE_ID}"
            response = requests.get(review_url, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Successfully reviewed profile {OVERSEER_PROFILE_ID}. Status: {response.status_code}")
            else:
                logger.warning(f"Failed to review profile {OVERSEER_PROFILE_ID}. Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during profile review: {e}")
        
        time.sleep(REVIEW_INTERVAL_SECONDS)

if __name__ == '__main__':
    run_admin_bot()
