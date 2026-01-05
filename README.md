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

## Status Check Utility (status_check.py)

This script is a lightweight watchdog to verify whether the network monitoring script is still running and actively logging data.

### What it does

Checks the last modified time of the CSV log file

Determines whether the monitor is:

✅ Running normally

❌ Stopped, stuck, or not updating

### How it works

The monitor script (speed_log.pyw) logs data every 30 minutes

status_check.py checks whether the CSV file was updated within an expected time window

If the file has not changed for more than the configured threshold, it flags a problem

### Configuration

Inside status_check.py:
```
FILE_PATH = "network_report_v2.csv"
MAX_DELAY_MINUTES = 40
```

MAX_DELAY_MINUTES should be greater than the monitor interval

Default values work well with a 30-minute monitor cycle

### Usage

Run manually:
```
python status_check.py
```

### When this is useful

Long-running monitoring sessions

Overnight or multi-day tests

Verifying the script didn’t stop due to sleep, crash, or reboot
