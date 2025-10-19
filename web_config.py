"""
Web Configuration Interface for 8x8 Weather Display
Provides a minimalist, modern UI to configure and monitor the display
"""

import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Global state to share with main application
class WebConfigState:
    """Shared state between web server and main application"""
    
    def __init__(self):
        self.display_manager = None
        self.scheduler = None
        self.enhanced_display = None
        self.update_intervals = {
            'weather': 1800,  # 30 minutes
            'earthquake': 300,  # 5 minutes
            'observation': 600  # 10 minutes
        }
        self.display_settings = {
            'mode': 'carousel',
            'page_duration': 15.0,
            'carousel_items': ['temperature_bars', 'weather_icon', 'temperature_display'],
            'brightness': 255
        }
        self.current_status = {
            'temperature': 0.0,
            'humidity': 0,
            'weather': 'N/A',
            'last_update': None,
            'running': False
        }

state = WebConfigState()


@app.route('/')
def index():
    """Main configuration page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current system status"""
    status = {
        'current_status': state.current_status,
        'display_settings': state.display_settings,
        'update_intervals': state.update_intervals,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add real-time data from display manager if available
    if state.enhanced_display:
        status['current_status'].update({
            'temperature': getattr(state.enhanced_display.observation_data, 'temperature', 0) if state.enhanced_display.observation_data else 0,
            'humidity': getattr(state.enhanced_display.observation_data, 'humidity', 0) if state.enhanced_display.observation_data else 0,
            'weather': getattr(state.enhanced_display.observation_data, 'weather', 'N/A') if state.enhanced_display.observation_data else 'N/A',
            'running': True
        })
    
    return jsonify(status)


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update display settings"""
    data = request.get_json()
    
    if 'display_settings' in data:
        state.display_settings.update(data['display_settings'])
        
        # Apply brightness change immediately
        if state.display_manager and 'brightness' in data['display_settings']:
            state.display_manager.device.contrast(data['display_settings']['brightness'])
    
    if 'update_intervals' in data:
        state.update_intervals.update(data['update_intervals'])
        
        # Apply update intervals to scheduler
        if state.scheduler:
            if 'weather' in data['update_intervals']:
                state.scheduler.weather_update_interval = data['update_intervals']['weather']
            if 'earthquake' in data['update_intervals']:
                state.scheduler.earthquake_check_interval = data['update_intervals']['earthquake']
            if 'observation' in data['update_intervals']:
                state.scheduler.observation_update_interval = data['update_intervals']['observation']
    
    return jsonify({'success': True, 'message': 'Settings updated'})


@app.route('/api/force_update', methods=['POST'])
def force_update():
    """Force immediate data update"""
    data = request.get_json()
    update_type = data.get('type', 'weather')
    
    if not state.scheduler:
        return jsonify({'success': False, 'message': 'Scheduler not initialized'})
    
    try:
        if update_type == 'weather':
            state.scheduler.force_weather_update()
        elif update_type == 'earthquake':
            state.scheduler.force_earthquake_check()
        
        return jsonify({'success': True, 'message': f'{update_type} update triggered'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/display_mode', methods=['POST'])
def change_display_mode():
    """Change display mode"""
    data = request.get_json()
    mode = data.get('mode', 'carousel')
    
    state.display_settings['mode'] = mode
    
    # Apply mode change if display manager is available
    if state.display_manager:
        # This would require extending display_manager with mode switching
        pass
    
    return jsonify({'success': True, 'message': f'Display mode changed to {mode}'})


def run_web_server(host='0.0.0.0', port=6666):
    """Run the web server in a separate thread"""
    app.run(host=host, port=port, debug=False, use_reloader=False)


def start_web_server(display_manager=None, scheduler=None, enhanced_display=None, host='0.0.0.0', port=6666):
    """Start the web server in a background thread"""
    state.display_manager = display_manager
    state.scheduler = scheduler
    state.enhanced_display = enhanced_display
    
    thread = threading.Thread(
        target=run_web_server,
        args=(host, port),
        daemon=True
    )
    thread.start()
    return thread


if __name__ == '__main__':
    # Run standalone for testing
    run_web_server()
