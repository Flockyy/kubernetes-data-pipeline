"""
Data Generator Service
Generates synthetic user activity events and sends them to the processor
"""

import os
import time
import json
import random
import logging
from datetime import datetime
import requests
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
PROCESSOR_URL = os.getenv('PROCESSOR_URL', 'http://data-processor:8000')
GENERATION_INTERVAL = float(os.getenv('GENERATION_INTERVAL', '2'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '5'))

fake = Faker()

# Event types and actions
EVENT_TYPES = ['page_view', 'click', 'purchase', 'login', 'logout', 'search']
DEVICE_TYPES = ['mobile', 'desktop', 'tablet']
BROWSERS = ['Chrome', 'Firefox', 'Safari', 'Edge']

def generate_event():
    """Generate a single user activity event"""
    event = {
        'event_id': fake.uuid4(),
        'user_id': fake.uuid4()[:8],
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': random.choice(EVENT_TYPES),
        'device_type': random.choice(DEVICE_TYPES),
        'browser': random.choice(BROWSERS),
        'session_id': fake.uuid4()[:12],
        'ip_address': fake.ipv4(),
        'country': fake.country_code(),
        'metadata': {
            'page_url': fake.url(),
            'referrer': fake.url() if random.random() > 0.3 else None,
            'duration_seconds': random.randint(1, 300)
        }
    }
    
    # Add type-specific data
    if event['event_type'] == 'purchase':
        event['metadata']['amount'] = round(random.uniform(10, 500), 2)
        event['metadata']['currency'] = 'USD'
        event['metadata']['product_id'] = fake.uuid4()[:8]
    elif event['event_type'] == 'search':
        event['metadata']['query'] = fake.sentence(nb_words=3)
    
    return event

def send_events(events):
    """Send events to the processor service"""
    try:
        response = requests.post(
            f"{PROCESSOR_URL}/process",
            json={'events': events},
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Successfully sent {len(events)} events to processor")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send events: {e}")
        return False

def health_check():
    """Check if processor is available"""
    try:
        response = requests.get(f"{PROCESSOR_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    logger.info("Data Generator starting...")
    logger.info(f"Processor URL: {PROCESSOR_URL}")
    logger.info(f"Generation interval: {GENERATION_INTERVAL}s")
    logger.info(f"Batch size: {BATCH_SIZE}")
    
    # Wait for processor to be ready
    logger.info("Waiting for processor to be ready...")
    while not health_check():
        logger.info("Processor not ready, waiting...")
        time.sleep(5)
    
    logger.info("Processor is ready! Starting event generation...")
    
    total_events = 0
    successful_batches = 0
    failed_batches = 0
    
    try:
        while True:
            # Generate batch of events
            events = [generate_event() for _ in range(BATCH_SIZE)]
            
            # Send to processor
            if send_events(events):
                successful_batches += 1
                total_events += len(events)
            else:
                failed_batches += 1
            
            # Log statistics
            if total_events % 50 == 0 and total_events > 0:
                logger.info(
                    f"Statistics - Total events: {total_events}, "
                    f"Successful batches: {successful_batches}, "
                    f"Failed batches: {failed_batches}"
                )
            
            time.sleep(GENERATION_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
