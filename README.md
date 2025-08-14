Falcon Health MonitorA comprehensive, self-restarting health monitor for NVIDIA Jetson devices. It logs system performance, network quality, and the status of local services and network devices to a local SQLite database. It also includes an optional, separate service to sync this data to a cloud provider.Table of ContentsKey FeaturesSetup and Installation1. Place Project Files2. Install Prerequisites3. Configure IPs and Services4. Install the Main Monitor ServiceCloud Sync Setup (Optional)How Cloud Sync WorksA. Install Cloud LibrariesB. Configure the Upload FunctionC. Install the Cloud Sync ServiceUsageManaging ServicesQuerying the DatabaseDeveloped ByKey FeaturesSystem Monitoring: Tracks CPU & GPU usage, CPU & GPU temperature, RAM, and Disk space utilization.Network Performance: Measures network latency, download, and upload speeds using speedtest-cli.IP Device Monitoring: Pings a list of user-defined IP devices (like cameras or servers) and logs their individual Online/Offline status.Local Service Monitoring: Checks the status (active/inactive) of any systemd services you specify in the configuration.Robust Database Logging: Inserts all metrics into a health_monitor.db SQLite database, providing a queryable history of system health.Reliable Operation: Runs as a systemd service, ensuring it starts automatically on boot and restarts if it ever fails.Cloud-Ready: Includes a separate, optional cloud_sync.py script to upload data to any cloud provider (AWS, GCP, custom API, etc.).Setup and Installation1. Place Project FilesCreate a directory on your Jetson (e.g., /home/jetson/falcon_monitor) and place all the project files inside it.2. Install PrerequisitesA helper script is provided to install the necessary tools.# Navigate to your project directory
cd /path/to/your/falcon_monitor

# Make the script executable
chmod +x install_prerequisites.sh

# Run the installer
sudo ./install_prerequisites.sh
3. Configure IPs and ServicesEdit the ips.json file to define what you want to monitor.devices: A dictionary of name: IP_address pairs for network devices.services: A list of systemd service names (e.g., docker.service).Example ips.json:{
  "devices": {
    "Front_Gate_Camera": "192.168.1.10",
    "Lobby_Camera": "192.168.1.11"
  },
  "services": [
    "docker.service",
    "falcon_monitor.service"
  ]
}
4. Install the Main Monitor ServiceTo run the main monitor reliably, install it as a systemd service.A. Edit the Service File:Open falcon_monitor.service. You must change WorkingDirectory and ExecStart to use the absolute path to your project directory.B. Install and Start the Service:# Copy the service file
sudo cp falcon_monitor.service /etc/systemd/system/falcon_monitor.service

# Reload systemd, enable the service to start on boot, and start it now
sudo systemctl daemon-reload
sudo systemctl enable falcon_monitor.service
sudo systemctl start falcon_monitor.service
Cloud Sync Setup (Optional)The cloud_sync.py script can run alongside the main monitor to send your data to a cloud provider.How Cloud Sync WorksThe script adds a synced_to_cloud flag to the local database. It periodically checks for unsynced records, bundles them into a JSON payload, and sends them to the cloud via the upload_data_to_cloud() function. If successful, it marks the records as synced to prevent duplicate uploads.A. Install Cloud LibrariesYou must install the Python library for your chosen provider.For a REST API: sudo python3 -m pip install requestsFor AWS S3: sudo python3 -m pip install boto3For Google Cloud Storage: sudo python3 -m pip install google-cloud-storageB. Configure the Upload FunctionOpen cloud_sync.py and find the function named upload_data_to_cloud.Uncomment the example block for your provider (REST API, AWS, or GCP).Fill in your specific details (API keys, bucket names, etc.).Use the examples as a template to build logic for other providers.C. Install the Cloud Sync ServiceFor reliable operation, run the sync script as its own service.A. Edit the Service File:Open cloud_sync.service and change WorkingDirectory and ExecStart to use the absolute path to your project directory.B. Install and Start the Service:# Copy the service file
sudo cp cloud_sync.service /etc/systemd/system/cloud_sync.service

# Reload systemd, enable, and start the service
sudo systemctl daemon-reload
sudo systemctl enable cloud_sync.service
sudo systemctl start cloud_sync.service
UsageManaging ServicesCheck Status: sudo systemctl status falcon_monitor.service or sudo systemctl status cloud_sync.serviceView Logs: sudo journalctl -u falcon_monitor.service -f or sudo journalctl -u cloud_sync.service -fStop Service: sudo systemctl stop <service_name>Restart Service: sudo systemctl restart <service_name>Querying the DatabaseAll data is stored in health_monitor.db.1. Install SQLite tool (if needed):sudo apt-get install -y sqlite32. Query data:# Open the database
sqlite3 health_monitor.db

# --- Inside the sqlite> prompt ---

# Improve formatting
.headers on
.mode column

# View the 5 most recent records
SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5;

# Exit
.exit
Developed ByRajesh RoyCTO at Assert AI and NVIDIA SpecialistEmail: rajeshroy402@gmail.comLinkedIn: linkedin.com/in/rajeshroy402
