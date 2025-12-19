"""
Data Processor Service
Receives events, processes/enriches them, and forwards to aggregator
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import requests
from collections import defaultdict
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
AGGREGATOR_URL = os.getenv('AGGREGATOR_URL', 'http://data-aggregator:8000')
PROCESSING_DELAY = float(os.getenv('PROCESSING_DELAY', '0.1'))

# Statistics
stats = {
    'events_received': 0,
    'events_processed': 0,
    'events_failed': 0,
    'last_event_time': None
}
stats_lock = threading.Lock()

def enrich_event(event):
    """Enrich event with additional processing"""
    processed_event = event.copy()
    
    # Add processing timestamp
    processed_event['processed_at'] = datetime.utcnow().isoformat()
    
    # Add derived fields
    processed_event['is_mobile'] = event.get('device_type') == 'mobile'
    processed_event['is_purchase'] = event.get('event_type') == 'purchase'
    
    # Calculate session duration bucket
    duration = event.get('metadata', {}).get('duration_seconds', 0)
    if duration < 30:
        processed_event['duration_bucket'] = 'short'
    elif duration < 180:
        processed_event['duration_bucket'] = 'medium'
    else:
        processed_event['duration_bucket'] = 'long'
    
    # Add risk score for purchases
    if processed_event['is_purchase']:
        amount = event.get('metadata', {}).get('amount', 0)
        processed_event['risk_score'] = min(100, int(amount / 10))
    
    return processed_event

def forward_to_aggregator(events):
    """Forward processed events to aggregator"""
    try:
        response = requests.post(
            f"{AGGREGATOR_URL}/aggregate",
            json={'events': events},
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Forwarded {len(events)} events to aggregator")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to forward to aggregator: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'data-processor'}), 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness check endpoint"""
    # Check if we can reach the aggregator
    try:
        response = requests.get(f"{AGGREGATOR_URL}/health", timeout=2)
        if response.status_code == 200:
            return jsonify({'status': 'ready'}), 200
    except:
        pass
    return jsonify({'status': 'not ready'}), 503

@app.route('/process', methods=['POST'])
def process_events():
    """Process incoming events"""
    try:
        data = request.get_json()
        events = data.get('events', [])
        
        if not events:
            return jsonify({'error': 'No events provided'}), 400
        
        with stats_lock:
            stats['events_received'] += len(events)
            stats['last_event_time'] = datetime.utcnow().isoformat()
        
        # Simulate processing time
        time.sleep(PROCESSING_DELAY)
        
        # Process and enrich events
        processed_events = []
        for event in events:
            try:
                processed_event = enrich_event(event)
                processed_events.append(processed_event)
            except Exception as e:
                logger.error(f"Failed to process event: {e}")
                with stats_lock:
                    stats['events_failed'] += 1
        
        # Forward to aggregator
        if processed_events:
            if forward_to_aggregator(processed_events):
                with stats_lock:
                    stats['events_processed'] += len(processed_events)
            else:
                with stats_lock:
                    stats['events_failed'] += len(processed_events)
        
        return jsonify({
            'status': 'success',
            'processed': len(processed_events),
            'failed': len(events) - len(processed_events)
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Return processing statistics"""
    with stats_lock:
        return jsonify(stats), 200

if __name__ == '__main__':
    logger.info("Data Processor starting...")
    logger.info(f"Aggregator URL: {AGGREGATOR_URL}")
    app.run(host='0.0.0.0', port=8000)
