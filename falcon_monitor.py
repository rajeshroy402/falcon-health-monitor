#!/usr/bin/env python3

import json
import os
import subprocess
import time
from datetime import datetime
import glob
import psutil
import sqlite3

IP_CONFIG_FILE = "ips.json"
DB_FILE = "health_monitor.db"
MONITOR_INTERVAL = 120

def print_credentials():
    print("+" + "-"*60 + "+")
    print("|" + "Falcon Health Monitor".center(60) + "|")
    print("|" + "Developed & Maintained By: Rajesh Roy".center(60) + "|")
    print("|" + "CTO at Assert AI and NVIDIA Specialist".center(60) + "|")
    print("|" + " ".center(60) + "|")
    print("|" + "Email: rajeshroy402@gmail.com".center(60) + "|")
    print("|" + "LinkedIn: www.linkedin.com/in/rajeshroy402".center(60) + "|")
    print("|" + " " * 60 + "|")
    print("+" + "-"*60 + "+")
    print("\n--- Starting Monitor ---\n")

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    db_columns = [
        'timestamp', 'cpu_usage_percent', 'cpu_temp_c', 'gpu_usage_percent', 'gpu_temp_c',
        'ram_usage_percent', 'disk_usage_percent', 'service_statuses', 'device_statuses',
        'network_latency_ms', 'download_mbps', 'upload_mbps'
    ]
    columns_sql = ", ".join([f'"{h}" TEXT' for h in db_columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS metrics ({columns_sql})")
    conn.commit()
    conn.close()

def push_to_database(data_dict):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        columns = ', '.join(data_dict.keys())
        placeholders = ', '.join(['?'] * len(data_dict))
        query = f"INSERT INTO metrics ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(data_dict.values()))
        conn.commit()
        conn.close()
        print(f"[{data_dict['timestamp']}] Data successfully pushed to database.")
    except Exception as e:
        print(f"ERROR: Failed to push data to database. {e}")

def get_temperatures():
    temps = {'CPU': 'N/A', 'GPU': 'N/A'}
    thermal_zone_names = {'cpu-thermal': 'CPU', 'gpu-thermal': 'GPU', 'AO-therm': 'CPU', 'GPU-therm': 'GPU'}
    try:
        for zone_path in glob.glob('/sys/class/thermal/thermal_zone*'):
            type_path, temp_path = os.path.join(zone_path, 'type'), os.path.join(zone_path, 'temp')
            if os.path.exists(type_path) and os.path.exists(temp_path):
                with open(type_path, 'r') as f: zone_type = f.read().strip()
                if zone_type in thermal_zone_names:
                    device_name = thermal_zone_names[zone_type]
                    with open(temp_path, 'r') as f: temperature = round(int(f.read().strip()) / 1000.0, 2)
                    temps[device_name] = temperature
    except Exception as e:
        print(f"ERROR: Reading temps failed. {e}")
    return temps

def get_gpu_usage():
    gpu_load_paths = ['/sys/devices/gpu.0/load', '/sys/class/devfreq/17000000.gpu/load']
    for path in gpu_load_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return round(int(f.read().strip()) / 10.0, 2)
            except Exception as e:
                print(f"ERROR: Reading GPU usage failed. {e}")
    return 'N/A'

def get_network_performance():
    print("🌐 Running network performance test...")
    try:
        command = ['speedtest-cli', '--json']
        # THE FIX: Removed 'text=True' and added manual decoding for full compatibility
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        output_str = result.stdout.decode('utf-8')
        data = json.loads(output_str)
        return {
            "latency": data.get('ping', 0),
            "download": data.get('download', 0) / 1e6,
            "upload": data.get('upload', 0) / 1e6
        }
    except FileNotFoundError:
        print("ERROR: 'speedtest-cli' command not found. Please ensure it is installed.")
        return None
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8').strip()
        print(f"ERROR: speedtest-cli failed with exit status {e.returncode}.")
        if error_message:
            print(f"--> Tool's error message: \"{error_message}\"")
        return None
    except json.JSONDecodeError:
        print("ERROR: Could not parse JSON output from speedtest-cli.")
        return None

def check_ip_status(ip_address):
    try:
        subprocess.run(['ping', '-c', '1', '-W', '2', ip_address], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 'Online'
    except Exception:
        return 'Offline'

def get_all_device_statuses(config):
    statuses = []
    devices_to_check = config.get('devices', {})
    if not isinstance(devices_to_check, dict):
        return ["'devices' key is not a dictionary"]
    for name, ip in devices_to_check.items():
        statuses.append(f"{name}: {check_ip_status(ip)}")
    return statuses

def check_service_status(service_name):
    try:
        subprocess.run(['systemctl', 'is-active', '--quiet', service_name], check=True)
        return 'active'
    except subprocess.CalledProcessError:
        return 'inactive'

def get_all_service_statuses(config):
    statuses = []
    services_to_check = config.get('services', [])
    if not isinstance(services_to_check, list):
        return ["'services' key is not a list"]
    for service in services_to_check:
        statuses.append(f"{service}: {check_service_status(service)}")
    return statuses

def run_monitor():
    print_credentials()
    setup_database()
    try:
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            config = {}
            if os.path.exists(IP_CONFIG_FILE):
                try:
                    with open(IP_CONFIG_FILE, 'r') as f:
                        config = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"ERROR: Could not parse JSON from '{IP_CONFIG_FILE}'. Check syntax. Details: {e}")

            temps = get_temperatures()
            system_metrics = {
                'cpu_usage_percent': psutil.cpu_percent(interval=1),
                'cpu_temp_c': temps.get('CPU', 'N/A'),
                'gpu_usage_percent': get_gpu_usage(),
                'gpu_temp_c': temps.get('GPU', 'N/A'),
                'ram_usage_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent
            }

            net_perf_data = get_network_performance()
            network_metrics = {'latency': 'N/A', 'download': 'N/A', 'upload': 'N/A'}
            if net_perf_data:
                network_metrics = {k: round(v, 2) for k, v in net_perf_data.items()}

            service_statuses_str = ' | '.join(get_all_service_statuses(config))
            device_statuses_str = ' | '.join(get_all_device_statuses(config))
            
            log_dict = {
                'timestamp': timestamp,
                'cpu_usage_percent': system_metrics['cpu_usage_percent'],
                'cpu_temp_c': system_metrics['cpu_temp_c'],
                'gpu_usage_percent': system_metrics['gpu_usage_percent'],
                'gpu_temp_c': system_metrics['gpu_temp_c'],
                'ram_usage_percent': system_metrics['ram_usage_percent'],
                'disk_usage_percent': system_metrics['disk_usage_percent'],
                'service_statuses': service_statuses_str,
                'device_statuses': device_statuses_str,
                'network_latency_ms': network_metrics['latency'],
                'download_mbps': network_metrics['download'],
                'upload_mbps': network_metrics['upload'],
            }
            
            push_to_database(log_dict)
            
            print(f"[{timestamp}] Logged stats successfully. Next check in 10 minutes.")
            
            time.sleep(MONITOR_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitor stopped by user.")
    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == "__main__":
    run_monitor()
