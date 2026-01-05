import speedtest
import csv
import time
import subprocess
import re
import platform
import statistics
from datetime import datetime, timezone, timedelta

# --- CONFIGURATION ---
CHECK_INTERVAL = 1800  # 30 Minutes
REPORT_FILE = "network_report_v2.csv"
TRACE_LOG_FILE = "traceroute_logs.txt"
MIN_SPEED_THRESHOLD = 50 

# Define IST Timezone
IST = timezone(timedelta(hours=5, minutes=30))

def run_traceroute(host):
    """Runs a traceroute to identify the exact hop where routing breaks."""
    system = platform.system().lower()
    cmd = ['tracert', '-d', '-h', '15', host] if system == 'windows' else ['traceroute', '-n', '-m', '15', host]
    
    try:
        # Timeout set to 120s to capture full path without crashing
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, _ = process.communicate(timeout=120)
        
        latencies = [float(x) for x in re.findall(r"(\d+) ms", out)]
        max_trace_lat = max(latencies) if latencies else 0
        hops = len(re.findall(r"^\s*\d+", out, re.MULTILINE))
        
        return hops, max_trace_lat, out
    except Exception as e:
        return 0, 0, f"Traceroute Failed: {e}"

def get_reliability_metrics(host="8.8.8.8"):
    """Checks basic connectivity (Ping) independent of Speedtest."""
    system = platform.system().lower()
    count_flag = "-n" if system == "windows" else "-c"
    
    try:
        process = subprocess.Popen(['ping', count_flag, '10', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, _ = process.communicate()
        
        latencies = [float(x) for x in re.findall(r"time[=<]([\d\.]+)\s*ms", out)]
        
        if "100% packet loss" in out or not latencies:
            return 0.0, 0.0, 0.0, 100.0
        
        sent_match = re.search(r"Sent = (\d+)", out) or re.search(r"(\d+) packets transmitted", out)
        recv_match = re.search(r"Received = (\d+)", out) or re.search(r"(\d+) received", out)
        
        loss_pct = 0.0
        if sent_match and recv_match:
            sent, recv = int(sent_match.group(1)), int(recv_match.group(1))
            loss_pct = round(((sent - recv) / sent) * 100, 2)
        
        return min(latencies), max(latencies), round(statistics.mean(latencies), 2), loss_pct
    except Exception:
        return 0.0, 0.0, 0.0, 100.0

def run_monitor():
    header = [
        "Timestamp_IST", "Status", "ISP", "Server_Name", "Server_Host", 
        "Download_Mbps", "Upload_Mbps", "Min_Lat", "Max_Lat", "Loss_Pct", 
        "Trace_Hops", "Trace_Max_Lat"
    ]

    try:
        with open(REPORT_FILE, 'x', newline='') as f:
            csv.writer(f).writerow(header)
    except FileExistsError:
        pass

    print(f"--- Smart Monitor v3.0 Active (Interval: {CHECK_INTERVAL}s) ---")
    print(f"--- Detecting: Full Outages vs. Partial Failures ---")

    try:
        while True:
            timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # 1. Try Full Speedtest
                st = speedtest.Speedtest() 
                st.get_best_server()
                server_name = st.results.server['name']
                server_host = st.results.server['host']
                target_ip = server_host.split(':')[0]

                down = st.download() / 1_000_000
                up = st.upload() / 1_000_000
                isp = st.get_config()['client']['isp']
                
                min_l, max_l, avg_l, loss = get_reliability_metrics() # Ping 8.8.8.8
                hops, trace_lat, trace_text = run_traceroute(target_ip) # Trace the specific server

                status = "PASS"
                if loss > 5 or avg_l > 150: status = "FAIL"
                elif down < MIN_SPEED_THRESHOLD: status = "WARN"

                # Log Success
                with open(REPORT_FILE, 'a', newline='') as f:
                    csv.writer(f).writerow([
                        timestamp, status, isp, server_name, target_ip, 
                        round(down, 2), round(up, 2), min_l, max_l, loss,
                        hops, trace_lat
                    ])

                # Log Trace
                with open(TRACE_LOG_FILE, 'a') as f:
                    f.write(f"\n--- {timestamp} | Server: {server_name} ({target_ip}) ---\n")
                    f.write(trace_text)
                    f.write("-" * 40 + "\n")
                
                print(f"[{timestamp}] {status} | {server_name} | {down:.1f} Mbps | Trace: {hops} hops")

            except Exception as e:
                # 2. IF SPEEDTEST CRASHES -> Run "Smart Diagnosis"
                err = str(e)
                log_status = "UNKNOWN"
                
                # Check if Internet is actually dead or just Speedtest servers are unreachable
                min_l, max_l, avg_l, loss = get_reliability_metrics("8.8.8.8")
                
                if loss == 100.0:
                    log_status = "OFFLINE" # Real Blackout
                    print(f"[{timestamp}] 🔴 CRITICAL: Total Internet Blackout.")
                else:
                    log_status = "PARTIAL_FAIL" # Internet works, but Routing/DNS is broken
                    print(f"[{timestamp}] ⚠️ PARTIAL SERVICE OUTAGE: Ping OK ({avg_l}ms), application traffic failing.")

                if "403" in err: 
                    log_status = "BLOCKED"

                # Write the "Zombie" or "Offline" status to CSV
                with open(REPORT_FILE, 'a', newline='') as f:
                    csv.writer(f).writerow([
                        timestamp, log_status, "N/A", "N/A", "N/A", 
                        0, 0, min_l, max_l, loss, 0, 0
                    ])
                
                # If banned, wait extra time
                if "403" in err: time.sleep(900)

            time.sleep(CHECK_INTERVAL) 

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    run_monitor()