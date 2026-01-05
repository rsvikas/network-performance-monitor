# Network Performance Monitor

This project helps detect:
- Partial internet outages
- High latency and jitter
- Routing instability
- Differences between full outages and degraded connectivity

## Features
- Periodic speed tests
- Ping-based reliability checks
- Traceroute logging
- CSV-based reporting
- Distinguishes OFFLINE vs PARTIAL failures

## Requirements
- Python 3.9+
- speedtest-cli

## Install dependencies:
```bash
pip install speedtest-cli
```
## Usage
### Start monitoring
```bash
python speed_log.pyw
```
### Generate report
```bash
python Speedtest_report.py
```
## Notes
Logs are generated locally and are ignored by git

Designed for troubleshooting ISP and routing issues

Can be affected by enterprise security tools (VPN / SWG)

Disclaimer
Use responsibly. This tool is for diagnostics and learning.
