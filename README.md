

````markdown
# Falcon Health Monitor

A comprehensive, self-restarting health monitor for NVIDIA Jetson devices. It logs system performance, network quality, and the status of local services and network devices to a local SQLite database. It also includes an optional, separate service to sync this data to a cloud provider.

## Table of Contents

-   [Key Features](#key-features)
-   [Setup and Installation](#setup-and-installation)
    -   [1. Place Project Files](#1-place-project-files)
    -   [2. Install Prerequisites](#2-install-prerequisites)
    -   [3. Configure IPs and Services](#3-configure-ips-and-services)
    -   [4. Install the Main Monitor Service](#4-install-the-main-monitor-service)
-   [Cloud Sync Setup (Optional)](#cloud-sync-setup-optional)
    -   [How Cloud Sync Works](#how-cloud-sync-works)
    -   [A. Install Cloud Libraries](#a-install-cloud-libraries)
    -   [B. Configure the Upload Function](#b-configure-the-upload-function)
    -   [C. Install the Cloud Sync Service](#c-install-the-cloud-sync-service)
-   [Usage](#usage)
    -   [Managing Services](#managing-services)
    -   [Querying the Database](#querying-the-database)
-   [Developed By](#developed-by)

---

## Key Features

-   **System Monitoring:** Tracks CPU & GPU usage, CPU & GPU temperature, RAM, and Disk space utilization.
-   **Network Performance:** Measures network latency, download, and upload speeds using `speedtest-cli`.
-   **IP Device Monitoring:** Pings a list of user-defined IP devices (like cameras or servers) and logs their individual Online/Offline status.
-   **Local Service Monitoring:** Checks the status (`active`/`inactive`) of any `systemd` services you specify in the configuration.
-   **Robust Database Logging:** Inserts all metrics into a `health_monitor.db` SQLite database, providing a queryable history of system health.
-   **Reliable Operation:** Runs as a `systemd` service, ensuring it starts automatically on boot and restarts if it ever fails.
-   **Cloud-Ready:** Includes a separate, optional `cloud_sync.py` script to upload data to any cloud provider (AWS, GCP, custom API, etc.).

---

## Setup and Installation

### 1. Place Project Files

Create a directory on your Jetson (e.g., `/home/jetson/falcon_monitor`) and place all the project files inside it.

### 2. Install Prerequisites

A helper script is provided to install the necessary tools.

```bash
# Navigate to your project directory
cd /path/to/your/falcon_monitor

# Make the script executable
chmod +x install_prerequisites.sh

# Run the installer
sudo ./install_prerequisites.sh
````

### 3\. Configure IPs and Services

Edit the `ips.json` file to define what you want to monitor.

  - `devices`: A dictionary of `name: IP_address` pairs for network devices.
  - `services`: A list of `systemd` service names (e.g., `docker.service`).

**Example `ips.json`:**

```json
{
  "devices": {
    "Front_Gate_Camera": "192.168.1.10",
    "Lobby_Camera": "192.168.1.11"
  },
  "services": [
    "docker.service",
    "falcon_monitor.service"
  ]
}
```

### 4\. Install the Main Monitor Service

To run the main monitor reliably, install it as a `systemd` service.

**A. Edit the Service File:**
Open `falcon_monitor.service`. You **must** change `WorkingDirectory` and `ExecStart` to use the **absolute path** to your project directory.

**B. Install and Start the Service:**

```bash
# Copy the service file
sudo cp falcon_monitor.service /etc/systemd/system/falcon_monitor.service

# Reload systemd, enable the service to start on boot, and start it now
sudo systemctl daemon-reload
sudo systemctl enable falcon_monitor.service
sudo systemctl start falcon_monitor.service
```

-----

## Cloud Sync Setup (Optional)

The `cloud_sync.py` script can run alongside the main monitor to send your data to a cloud provider.

### How Cloud Sync Works

The script adds a `synced_to_cloud` flag to the local database. It periodically checks for unsynced records, bundles them into a JSON payload, and sends them to the cloud via the `upload_data_to_cloud()` function. If successful, it marks the records as synced to prevent duplicate uploads.

### A. Install Cloud Libraries

You must install the Python library for your chosen provider.

  - **For a REST API:** `sudo python3 -m pip install requests`
  - **For AWS S3:** `sudo python3 -m pip install boto3`
  - **For Google Cloud Storage:** `sudo python3 -m pip install google-cloud-storage`

### B. Configure the Upload Function

Open `cloud_sync.py` and find the function named `upload_data_to_cloud`.

  - Uncomment the example block for your provider (REST API, AWS, or GCP).
  - Fill in your specific details (API keys, bucket names, etc.).
  - Use the examples as a template to build logic for other providers.

### C. Install the Cloud Sync Service

For reliable operation, run the sync script as its own service.

**A. Edit the Service File:**
Open `cloud_sync.service` and change `WorkingDirectory` and `ExecStart` to use the **absolute path** to your project directory.

**B. Install and Start the Service:**

```bash
# Copy the service file
sudo cp cloud_sync.service /etc/systemd/system/cloud_sync.service

# Reload systemd, enable, and start the service
sudo systemctl daemon-reload
sudo systemctl enable cloud_sync.service
sudo systemctl start cloud_sync.service
```

-----

## Usage

### Managing Services

  - **Check Status:** `sudo systemctl status falcon_monitor.service` or `sudo systemctl status cloud_sync.service`
  - **View Logs:** `sudo journalctl -u falcon_monitor.service -f` or `sudo journalctl -u cloud_sync.service -f`
  - **Stop Service:** `sudo systemctl stop <service_name>`
  - **Restart Service:** `sudo systemctl restart <service_name>`

### Querying the Database

All data is stored in `health_monitor.db`.

**1. Install SQLite tool (if needed):**
`sudo apt-get install -y sqlite3`

**2. Query data:**

```bash
# Open the database
sqlite3 health_monitor.db

# --- Inside the sqlite> prompt ---

# Improve formatting
.headers on
.mode column

# View the 5 most recent records
SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5;

# Exit
.exit
```

-----

## Developed By

  - **Rajesh Roy**
  - CTO at Assert AI and NVIDIA Specialist
  - **Email:** `rajeshroy402@gmail.com`
  - **LinkedIn:** [linkedin.com/in/rajeshroy402](https://www.google.com/search?q=https://www.linkedin.com/in/rajeshroy402)

<!-- end list -->

```
```
