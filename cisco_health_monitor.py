#!/usr/bin/env python3
"""
Cisco 9300 Switch Health Monitor
This script reads the YAML configuration and executes health checks on Cisco 9300 switches.

Requirements:
    pip install netmiko pyyaml textfsm pyats genie
"""

import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

try:
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
except ImportError:
    print("Please install netmiko: pip install netmiko")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CiscoHealthMonitor:
    """Cisco 9300 Switch Health Monitoring Class"""
    
    def __init__(self, config_file: str = 'cisco_9300_health_check.yaml'):
        """Initialize the health monitor with YAML config"""
        self.config = self._load_config(config_file)
        self.results = {}
        self.connection = None
        
    def _load_config(self, config_file: str) -> Dict:
        """Load YAML configuration file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file {config_file} not found")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            raise
    
    def connect_to_device(self, host: str, username: str, password: str, 
                          secret: str = None) -> bool:
        """Establish connection to Cisco switch"""
        device_params = {
            'device_type': self.config['connection']['device_type'],
            'host': host,
            'username': username,
            'password': password,
            'timeout': self.config['connection']['timeout'],
            'global_delay_factor': self.config['connection']['global_delay_factor'],
        }
        
        if secret:
            device_params['secret'] = secret
        
        try:
            logger.info(f"Connecting to {host}...")
            self.connection = ConnectHandler(**device_params)
            
            # Enter enable mode if secret is provided
            if secret:
                self.connection.enable()
            
            logger.info(f"Successfully connected to {host}")
            return True
            
        except NetmikoTimeoutException:
            logger.error(f"Timeout connecting to {host}")
            return False
        except NetmikoAuthenticationException:
            logger.error(f"Authentication failed for {host}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to {host}: {str(e)}")
            return False
    
    def execute_health_check(self, check_name: str) -> Dict:
        """Execute a specific health check"""
        if not self.connection:
            logger.error("No active connection to device")
            return {}
        
        health_check = self.config['health_checks'].get(check_name)
        if not health_check or not health_check.get('enabled'):
            logger.warning(f"Health check '{check_name}' not enabled or not found")
            return {}
        
        logger.info(f"Executing {check_name} health check...")
        check_results = {
            'check_name': check_name,
            'timestamp': datetime.now().isoformat(),
            'commands': []
        }
        
        for cmd_config in health_check.get('commands', []):
            command = cmd_config['command']
            description = cmd_config.get('description', '')
            
            try:
                logger.info(f"Executing: {command}")
                output = self.connection.send_command(
                    command,
                    use_textfsm=cmd_config.get('parse', False)
                )
                
                check_results['commands'].append({
                    'command': command,
                    'description': description,
                    'output': output,
                    'status': 'success'
                })
                
            except Exception as e:
                logger.error(f"Error executing {command}: {str(e)}")
                check_results['commands'].append({
                    'command': command,
                    'description': description,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return check_results
    
    def execute_all_health_checks(self) -> Dict:
        """Execute all enabled health checks"""
        logger.info("Starting all health checks...")
        
        all_results = {
            'device_info': self.config['switch_info'],
            'execution_time': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Execute each health check
        for check_name in self.config['health_checks'].keys():
            result = self.execute_health_check(check_name)
            if result:
                all_results['checks'][check_name] = result
        
        self.results = all_results
        return all_results
    
    def save_results(self, output_dir: str = None) -> str:
        """Save results to file"""
        if not self.results:
            logger.warning("No results to save")
            return None
        
        # Use configured output path or provided path
        output_config = self.config.get('output', {})
        if output_dir is None:
            output_dir = output_config.get('file_path', './output')
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cisco9300_health_{timestamp}.json"
        filepath = Path(output_dir) / filename
        
        # Save results
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Results saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return None
    
    def disconnect(self):
        """Disconnect from device"""
        if self.connection:
            self.connection.disconnect()
            logger.info("Disconnected from device")
    
    def analyze_thresholds(self) -> Dict:
        """Analyze results against configured thresholds"""
        alerts = []
        
        # This is a placeholder for threshold analysis
        # You would implement specific logic based on your monitoring needs
        
        return {'alerts': alerts}


def main():
    """
    Main execution function
    
    Usage:
        python cisco_health_monitor.py
    
    Environment Variables:
        SWITCH_HOST: IP address or hostname of the switch
        SWITCH_USER: Username for authentication
        SWITCH_PASS: Password for authentication
        SWITCH_SECRET: Enable secret (optional)
    """
    import os
    
    # Get connection details from environment variables or prompt
    host = os.getenv('SWITCH_HOST') or input("Switch IP/Hostname: ")
    username = os.getenv('SWITCH_USER') or input("Username: ")
    password = os.getenv('SWITCH_PASS') or input("Password: ")
    secret = os.getenv('SWITCH_SECRET') or input("Enable Secret (press Enter to skip): ")
    
    # Initialize monitor
    monitor = CiscoHealthMonitor('cisco_9300_health_check.yaml')
    
    try:
        # Connect to device
        if not monitor.connect_to_device(host, username, password, secret or None):
            logger.error("Failed to connect to device")
            return
        
        # Execute all health checks
        results = monitor.execute_all_health_checks()
        
        # Save results
        output_file = monitor.save_results()
        if output_file:
            print(f"\nHealth check completed. Results saved to: {output_file}")
        
        # Analyze thresholds
        analysis = monitor.analyze_thresholds()
        if analysis.get('alerts'):
            print("\nAlerts detected:")
            for alert in analysis['alerts']:
                print(f"  - {alert}")
        
    except KeyboardInterrupt:
        logger.info("Health check interrupted by user")
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
    finally:
        # Disconnect
        monitor.disconnect()


if __name__ == '__main__':
    main()
