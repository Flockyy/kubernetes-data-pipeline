"""
Data Aggregator Service
Aggregates processed events and exposes metrics
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from collections import defaultdict, Counter
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
CLEANUP_INTERVAL = int(os.getenv('CLEANUP_INTERVAL', '300'))  # 5 minutes
RETENTION_SECONDS = int(os.getenv('RETENTION_SECONDS', '3600'))  # 1 hour

# Aggregated data storage
aggregated_data = {
    'total_events': 0,
    'events_by_type': Counter(),
    'events_by_device': Counter(),
    'events_by_country': Counter(),
    'purchases': {
        'count': 0,
        'total_revenue': 0.0,
        'avg_amount': 0.0
    },
    'user_sessions': defaultdict(list),
    'recent_events': [],
    'start_time': datetime.utcnow().isoformat(),
    'last_update': None
}
data_lock = threading.Lock()

def cleanup_old_events():
    """Background thread to cleanup old events"""
    while True:
        time.sleep(CLEANUP_INTERVAL)
        with data_lock:
            cutoff_time = datetime.utcnow() - timedelta(seconds=RETENTION_SECONDS)
            
            # Clean recent events
            aggregated_data['recent_events'] = [
                e for e in aggregated_data['recent_events']
                if datetime.fromisoformat(e['timestamp']) > cutoff_time
            ]
            
            # Clean user sessions
            for user_id in list(aggregated_data['user_sessions'].keys()):
                aggregated_data['user_sessions'][user_id] = [
                    e for e in aggregated_data['user_sessions'][user_id]
                    if datetime.fromisoformat(e['timestamp']) > cutoff_time
                ]
                if not aggregated_data['user_sessions'][user_id]:
                    del aggregated_data['user_sessions'][user_id]
            
            logger.info("Cleaned up old events")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_events, daemon=True)
cleanup_thread.start()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'data-aggregator'}), 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness check endpoint"""
    return jsonify({'status': 'ready'}), 200

@app.route('/aggregate', methods=['POST'])
def aggregate_events():
    """Aggregate incoming processed events"""
    try:
        data = request.get_json()
        events = data.get('events', [])
        
        if not events:
            return jsonify({'error': 'No events provided'}), 400
        
        with data_lock:
            for event in events:
                # Update counters
                aggregated_data['total_events'] += 1
                aggregated_data['events_by_type'][event.get('event_type', 'unknown')] += 1
                aggregated_data['events_by_device'][event.get('device_type', 'unknown')] += 1
                aggregated_data['events_by_country'][event.get('country', 'unknown')] += 1
                
                # Track purchases
                if event.get('is_purchase'):
                    amount = event.get('metadata', {}).get('amount', 0)
                    aggregated_data['purchases']['count'] += 1
                    aggregated_data['purchases']['total_revenue'] += amount
                    aggregated_data['purchases']['avg_amount'] = (
                        aggregated_data['purchases']['total_revenue'] / 
                        aggregated_data['purchases']['count']
                    )
                
                # Track user sessions
                user_id = event.get('user_id')
                if user_id:
                    aggregated_data['user_sessions'][user_id].append({
                        'timestamp': event.get('timestamp'),
                        'event_type': event.get('event_type')
                    })
                
                # Keep recent events (limited to last 100)
                aggregated_data['recent_events'].append({
                    'timestamp': event.get('timestamp'),
                    'event_type': event.get('event_type'),
                    'user_id': user_id,
                    'device_type': event.get('device_type')
                })
                if len(aggregated_data['recent_events']) > 100:
                    aggregated_data['recent_events'].pop(0)
            
            aggregated_data['last_update'] = datetime.utcnow().isoformat()
        
        logger.info(f"Aggregated {len(events)} events")
        return jsonify({'status': 'success', 'aggregated': len(events)}), 200
        
    except Exception as e:
        logger.error(f"Error aggregating events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Return aggregated metrics"""
    with data_lock:
        metrics = {
            'total_events': aggregated_data['total_events'],
            'events_by_type': dict(aggregated_data['events_by_type']),
            'events_by_device': dict(aggregated_data['events_by_device']),
            'events_by_country': dict(aggregated_data['events_by_country'].most_common(10)),
            'purchases': aggregated_data['purchases'].copy(),
            'active_users': len(aggregated_data['user_sessions']),
            'recent_events_count': len(aggregated_data['recent_events']),
            'start_time': aggregated_data['start_time'],
            'last_update': aggregated_data['last_update']
        }
    
    return jsonify(metrics), 200

@app.route('/metrics/html', methods=['GET'])
def get_metrics_html():
    """Return formatted HTML metrics dashboard"""
    with data_lock:
        metrics = {
            'total_events': aggregated_data['total_events'],
            'events_by_type': dict(aggregated_data['events_by_type']),
            'events_by_device': dict(aggregated_data['events_by_device']),
            'events_by_country': dict(aggregated_data['events_by_country'].most_common(10)),
            'purchases': aggregated_data['purchases'].copy(),
            'active_users': len(aggregated_data['user_sessions']),
            'recent_events': aggregated_data['recent_events'][-20:],
            'start_time': aggregated_data['start_time'],
            'last_update': aggregated_data['last_update']
        }
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Pipeline Metrics</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .metric-card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
            .metric-value { font-size: 32px; color: #007bff; font-weight: bold; }
            .metric-list { list-style: none; padding: 0; }
            .metric-list li { padding: 5px 0; border-bottom: 1px solid #eee; }
            .header { text-align: center; padding: 20px; background: #007bff; color: white; border-radius: 8px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .refresh { text-align: center; margin: 20px 0; }
            .refresh button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            .refresh button:hover { background: #0056b3; }
        </style>
        <script>
            function refreshPage() { location.reload(); }
            setTimeout(refreshPage, 30000); // Auto-refresh every 30 seconds
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Kubernetes Data Pipeline Metrics</h1>
                <p>Real-time Analytics Dashboard</p>
            </div>
            
            <div class="refresh">
                <button onclick="refreshPage()">🔄 Refresh Now</button>
                <p style="color: #666; font-size: 12px;">Auto-refreshes every 30 seconds</p>
            </div>
            
            <div class="grid">
                <div class="metric-card">
                    <div class="metric-title">Total Events Processed</div>
                    <div class="metric-value">{{ metrics.total_events }}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Active Users</div>
                    <div class="metric-value">{{ metrics.active_users }}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Total Revenue</div>
                    <div class="metric-value">${{ "%.2f"|format(metrics.purchases.total_revenue) }}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Purchases</div>
                    <div class="metric-value">{{ metrics.purchases.count }}</div>
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Events by Type</div>
                <ul class="metric-list">
                    {% for type, count in metrics.events_by_type.items() %}
                    <li><strong>{{ type }}</strong>: {{ count }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Events by Device</div>
                <ul class="metric-list">
                    {% for device, count in metrics.events_by_device.items() %}
                    <li><strong>{{ device }}</strong>: {{ count }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Top Countries</div>
                <ul class="metric-list">
                    {% for country, count in metrics.events_by_country.items() %}
                    <li><strong>{{ country }}</strong>: {{ count }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">System Info</div>
                <ul class="metric-list">
                    <li><strong>Start Time:</strong> {{ metrics.start_time }}</li>
                    <li><strong>Last Update:</strong> {{ metrics.last_update }}</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, metrics=metrics)

if __name__ == '__main__':
    logger.info("Data Aggregator starting...")
    app.run(host='0.0.0.0', port=8000)
