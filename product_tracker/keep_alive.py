"""
Keep-Alive Service for Render Deployment

This module implements multiple strategies to keep the Render application active:
1. Internal self-ping scheduler
2. Health check monitoring
3. External ping coordination
4. Scheduler restart protection
"""

import os
import time
import requests
import threading
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self):
        self.scheduler = None
        self.app_url = None
        self.is_production = os.environ.get('ENVIRONMENT') == 'production'
        self.ping_interval = 10  # minutes
        self.last_ping = None
        self.failed_pings = 0
        self.max_failed_pings = 3
        
        # Only run in production (Render)
        if self.is_production:
            self._setup_production_monitoring()
    
    def _setup_production_monitoring(self):
        """Set up keep-alive monitoring for production"""
        # Get app URL from Render environment with multiple fallback strategies
        # Method 1: Try RENDER_EXTERNAL_URL (most reliable on Render)
        self.app_url = os.environ.get('RENDER_EXTERNAL_URL')
        
        if not self.app_url:
            # Method 2: Try RENDER_SERVICE_NAME (may not be available)
            render_service_name = os.environ.get('RENDER_SERVICE_NAME')
            if render_service_name:
                self.app_url = f"https://{render_service_name}.onrender.com"
        
        if not self.app_url:
            # Method 3: Hardcoded fallback for known deployment
            self.app_url = "https://product-cost-tracker-b7xd.onrender.com"
            
        logger.info(f"Keep-alive service initialized with URL: {self.app_url}")
        
        # Start background scheduler for self-ping
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=self._self_ping,
            trigger='interval',
            minutes=self.ping_interval,
            id='keep_alive_ping',
            replace_existing=True
        )
        
        # Add health check job
        self.scheduler.add_job(
            func=self._health_monitor,
            trigger='interval',
            minutes=5,
            id='health_monitor',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"✅ Keep-alive service started for {self.app_url}")
    
    def _self_ping(self):
        """Ping own application to keep it awake"""
        if not self.app_url:
            return
            
        try:
            # Ping the keep-alive endpoint
            response = requests.get(
                f"{self.app_url}/keep-alive",
                timeout=30,
                headers={'User-Agent': 'KeepAlive-Internal/1.0'}
            )
            
            if response.status_code == 200:
                self.last_ping = datetime.now()
                self.failed_pings = 0
                logger.info(f"✅ Keep-alive ping successful at {self.last_ping}")
            else:
                self._handle_ping_failure(f"HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self._handle_ping_failure(str(e))
    
    def _handle_ping_failure(self, error):
        """Handle ping failures with retry logic"""
        self.failed_pings += 1
        logger.warning(f"⚠️ Keep-alive ping failed ({self.failed_pings}/{self.max_failed_pings}): {error}")
        
        if self.failed_pings >= self.max_failed_pings:
            logger.error(f"❌ Keep-alive service failing after {self.failed_pings} attempts")
            # Could implement additional recovery strategies here
    
    def _health_monitor(self):
        """Monitor application health and scheduler status"""
        try:
            # Check if main scheduler is still running
            from product_tracker.scheduler import get_scheduler_status
            scheduler_status = get_scheduler_status()
            
            if not scheduler_status.get('running', False):
                logger.warning("⚠️ Main scheduler appears to be stopped, attempting restart...")
                # Attempt to restart scheduler
                from product_tracker.scheduler import start_scheduler
                start_scheduler()
                
        except Exception as e:
            logger.error(f"❌ Health monitor error: {e}")
    
    def get_status(self):
        """Get current keep-alive service status"""
        return {
            'enabled': self.is_production,
            'app_url': self.app_url,
            'ping_interval_minutes': self.ping_interval,
            'last_ping': self.last_ping.isoformat() if self.last_ping else None,
            'failed_pings': self.failed_pings,
            'scheduler_running': self.scheduler.running if self.scheduler else False
        }
    
    def stop(self):
        """Stop the keep-alive service"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🔌 Keep-alive service stopped")

# Global keep-alive service instance
keep_alive_service = KeepAliveService()

def get_keep_alive_status():
    """Get keep-alive service status"""
    return keep_alive_service.get_status()

def stop_keep_alive_service():
    """Stop keep-alive service"""
    keep_alive_service.stop()

# External Keep-Alive Services Configuration
EXTERNAL_MONITORING_SERVICES = [
    {
        'name': 'UptimeRobot',
        'description': 'Free monitoring service (50 monitors)',
        'setup_url': 'https://uptimerobot.com/',
        'instructions': [
            '1. Create free account at uptimerobot.com',
            '2. Add new monitor: HTTP(s)',
            '3. URL: https://your-app.onrender.com/health',
            '4. Monitoring interval: 5 minutes',
            '5. Enable notifications via email/webhook'
        ]
    },
    {
        'name': 'Pingdom',
        'description': 'Free tier with basic monitoring',
        'setup_url': 'https://www.pingdom.com/',
        'instructions': [
            '1. Sign up for free Pingdom account',
            '2. Create new uptime check',
            '3. URL: https://your-app.onrender.com/health',
            '4. Check interval: 5 minutes',
            '5. Set up alerting preferences'
        ]
    },
    {
        'name': 'StatusCake',
        'description': 'Free monitoring with unlimited tests',
        'setup_url': 'https://www.statuscake.com/',
        'instructions': [
            '1. Create StatusCake account',
            '2. Add new uptime test',
            '3. URL: https://your-app.onrender.com/keep-alive',
            '4. Test frequency: Every 5 minutes',
            '5. Configure contact groups for alerts'
        ]
    }
]

def get_external_monitoring_options():
    """Get list of external monitoring service options"""
    return EXTERNAL_MONITORING_SERVICES
