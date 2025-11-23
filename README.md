# Cisco 9300 Switch Health Monitoring

A comprehensive YAML-based configuration and Python automation tool for monitoring Cisco Catalyst 9300 series switches. This repository provides automated health checks for power supply, stack status, stack ports, fans, CPU, memory, and temperature.

## 🚀 Features

- **Power Supply Monitoring**: Track power supply status, PoE power, and environmental conditions
- **Stack Status Monitoring**: Monitor stack member states, roles, and priorities
- **Stack Ports Monitoring**: Check stack port status, bandwidth, and link health
- **Fan Status Monitoring**: Track fan speeds, states, and failures
- **CPU Monitoring**: Monitor CPU utilization with historical data
- **Memory Monitoring**: Track memory usage and identify memory leaks
- **Temperature Monitoring**: Monitor temperature sensors and thresholds
- **Configurable Thresholds**: Set custom warning and critical thresholds
- **Multiple Output Formats**: JSON, YAML, and text output support
- **Alert Integration**: Email, Syslog, and SNMP trap support

## 📋 Prerequisites

### Required Python Packages

```bash
pip install netmiko pyyaml textfsm pyats genie
```

### Cisco IOS-XE Version
- Cisco Catalyst 9300 series switches
- IOS-XE 16.x or later recommended

### Network Access
- SSH access to Cisco switches (port 22)
- Enable privilege level 15 or appropriate TACACS/RADIUS permissions

## 📁 Repository Structure

```
cisco-switch-monitoring/
├── cisco_9300_health_check.yaml    # Main YAML configuration
├── cisco_health_monitor.py         # Python monitoring script
├── README.md                       # This file
└── output/                         # Results directory (auto-created)
```

## ⚙️ Configuration

### YAML Configuration File

The `cisco_9300_health_check.yaml` file contains all monitoring configurations:

#### Main Sections:

1. **Connection Parameters**: Device type, timeout, and delay settings
2. **Health Checks**: Individual monitoring modules
   - Power Supply
   - Stack Status
   - Stack Ports
   - Fan Status
   - CPU Status
   - Memory Status
   - Temperature Status
3. **Monitoring Schedule**: Polling intervals and alert configuration
4. **Output Configuration**: File paths, formats, and retention
5. **Parsing Rules**: TextFSM and Genie parser settings
6. **Error Handling**: Retry logic and error management

#### Key Commands by Category:

**Power Supply:**
- `show environment power all`
- `show power inline`
- `show environment status`

**Stack Status:**
- `show switch`
- `show switch detail`
- `show switch stack-ring speed`
- `show platform stack manager all`

**Stack Ports:**
- `show switch stack-ports`
- `show switch stack-ports summary`
- `show platform stack manager stack-ports`

**Fan Status:**
- `show environment fan`
- `show environment status`
- `show environment all`

**CPU Status:**
- `show processes cpu sorted`
- `show processes cpu history`
- `show processes cpu platform sorted`
- `show platform software status control-processor brief`

**Memory Status:**
- `show processes memory sorted`
- `show platform software status control-processor brief`

**Temperature:**
- `show environment temperature`
- `show environment status`

## 🔧 Usage

### Method 1: Using Environment Variables

```bash
export SWITCH_HOST="192.168.1.1"
export SWITCH_USER="admin"
export SWITCH_PASS="your_password"
export SWITCH_SECRET="your_enable_secret"

python cisco_health_monitor.py
```

### Method 2: Interactive Mode

```bash
python cisco_health_monitor.py
```

The script will prompt for:
- Switch IP/Hostname
- Username
- Password
- Enable Secret (optional)

### Method 3: Programmatic Usage

```python
from cisco_health_monitor import CiscoHealthMonitor

# Initialize monitor
monitor = CiscoHealthMonitor('cisco_9300_health_check.yaml')

# Connect to device
monitor.connect_to_device(
    host='192.168.1.1',
    username='admin',
    password='password',
    secret='enable_secret'
)

# Execute all health checks
results = monitor.execute_all_health_checks()

# Save results
monitor.save_results()

# Disconnect
monitor.disconnect()
```

## 📊 Output Examples

### JSON Output Format

```json
{
  "device_info": {
    "model": "Cisco Catalyst 9300",
    "description": "Health monitoring configuration"
  },
  "execution_time": "2025-11-23T23:10:00",
  "checks": {
    "power_supply": {
      "check_name": "power_supply",
      "timestamp": "2025-11-23T23:10:05",
      "commands": [
        {
          "command": "show environment power all",
          "description": "Display all power supply status",
          "output": "...",
          "status": "success"
        }
      ]
    }
  }
}
```

## 🔔 Alert Configuration

### Email Alerts

Edit the YAML configuration:

```yaml
alerts:
  email:
    enabled: true
    recipients:
      - "netops@example.com"
      - "oncall@example.com"
```

### Syslog Integration

```yaml
alerts:
  syslog:
    enabled: true
    server: "syslog.company.com"
    port: 514
```

### SNMP Traps

```yaml
alerts:
  snmp:
    enabled: true
    trap_server: "snmp.company.com"
```

## 🎯 Threshold Configuration

Customize thresholds in the YAML file:

```yaml
health_checks:
  cpu:
    thresholds:
      warning_percent: 80
      critical_percent: 95
  
  fan:
    thresholds:
      rpm_warning: 5000
      rpm_critical: 3000
  
  temperature:
    thresholds:
      warning_celsius: 65
      critical_celsius: 75
```

## 🔄 Scheduling with Cron

Add to crontab for automated monitoring:

```bash
# Run health check every 5 minutes
*/5 * * * * cd /path/to/repo && /usr/bin/python3 cisco_health_monitor.py

# Run health check every hour
0 * * * * cd /path/to/repo && /usr/bin/python3 cisco_health_monitor.py

# Run health check daily at 2 AM
0 2 * * * cd /path/to/repo && /usr/bin/python3 cisco_health_monitor.py
```

## 📈 Integration Options

### InfluxDB Integration

```yaml
output:
  database:
    enabled: true
    type: "influxdb"
    host: "localhost"
    port: 8086
    database_name: "network_monitoring"
```

### Prometheus Integration

```yaml
output:
  database:
    enabled: true
    type: "prometheus"
    host: "localhost"
    port: 9090
```

### Elasticsearch Integration

```yaml
output:
  database:
    enabled: true
    type: "elasticsearch"
    host: "localhost"
    port: 9200
    database_name: "cisco-monitoring"
```

## 🛠️ Customization

### Adding Custom Commands

Edit the YAML configuration to add new commands:

```yaml
health_checks:
  custom_check:
    enabled: true
    commands:
      - command: "show version"
        description: "Display device version"
        parse: true
      - command: "show inventory"
        description: "Display hardware inventory"
        parse: true
    output_format: "json"
```

### Creating Custom Parsers

Add custom TextFSM parsers:

```yaml
parsing:
  use_textfsm: true
  custom_parsers:
    my_custom_check: "parsers/my_parser.py"
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Verify network connectivity
   - Check SSH access and firewall rules
   - Increase timeout in YAML config

2. **Authentication Failed**
   - Verify credentials
   - Check AAA configuration on switch
   - Ensure proper privilege level

3. **Command Not Recognized**
   - Verify IOS-XE version
   - Check if command is available on your platform
   - Review switch capabilities

4. **Parsing Errors**
   - Update TextFSM templates
   - Disable parsing for specific commands
   - Use raw text output for debugging

## 📝 Best Practices

1. **Security**
   - Use environment variables for credentials
   - Implement vault solutions for password management
   - Use SSH keys where possible

2. **Performance**
   - Adjust polling intervals based on network size
   - Use appropriate timeouts
   - Implement rate limiting

3. **Maintenance**
   - Regularly review and update thresholds
   - Archive old logs based on retention policy
   - Keep parsers updated with IOS-XE versions

4. **Monitoring**
   - Set up alerts for critical issues
   - Review logs regularly
   - Implement trending and reporting

## 📚 Additional Resources

- [Cisco Catalyst 9300 Configuration Guide](https://www.cisco.com/c/en/us/support/switches/catalyst-9300-series-switches/products-installation-and-configuration-guides-list.html)
- [Netmiko Documentation](https://github.com/ktbyers/netmiko)
- [TextFSM Templates](https://github.com/networktocode/ntc-templates)
- [Genie Documentation](https://developer.cisco.com/docs/genie-docs/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available for use in network automation projects.

## 👤 Author

**Mylappan**
- GitHub: [@mylappaninfra](https://github.com/mylappaninfra)
- Experience: 12+ years in network domain
- Specialization: Network Architecture, SD-WAN Technology

## 🔗 Repository

[https://github.com/mylappaninfra/cisco-switch-monitoring](https://github.com/mylappaninfra/cisco-switch-monitoring)

---

**Note**: This tool is designed for Cisco Catalyst 9300 series switches. Some commands may need modification for other platforms.
