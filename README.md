Falcon Health MonitorA comprehensive, self-restarting health monitor for NVIDIA Jetson devices. It logs system performance, network quality, the status of local services, and the status of network devices to a local SQLite database.Key FeaturesSystem Monitoring: Tracks CPU & GPU usage, CPU & GPU temperature, RAM, and Disk space utilization.Network Performance: Measures network latency, download, and upload speeds using speedtest-cli.IP Device Monitoring: Pings a list of user-defined IP devices (like cameras or servers) and logs their individual Online/Offline status.Local Service Monitoring: Checks the status (active/inactive) of any systemd services you specify in the configuration.Database Logging: Inserts all metrics into a health_monitor.db SQLite database, providing a robust, queryable history of system health.Reliable Operation: Runs as a systemd service, ensuring it starts automatically on boot and restarts if it ever fails.Developer Ready: Includes a push_to_database function that can be easily modified by a developer to integrate with other database systems like PostgreSQL or MySQL.Setup and Installation1. PrerequisitesFirst, you need to install the required tools. A helper script is provided for this. Place install_prerequisites.sh in your project directory and run the following commands:# Navigate to your project directory
cd /path/to/your/falcon_monitor

# Make the script executable
chmod +x install_prerequisites.sh

# Run the installer
sudo ./install_prerequisites.sh
2. ConfigurationThe monitor is configured using the ips.json file. This file allows you to specify which network devices and local services to monitor.devices: A dictionary of name: IP_address pairs for network devices you want to ping.services: A list of systemd service names (e.g., docker.service) you want to track.Example ips.json:{
  "devices": {
    "Front_Gate_Camera": "192.168.1.10",
    "Lobby_Camera": "192.168.1.11",
    "Main_Server": "192.168.1.2"
  },
  "services": [
    "docker.service",
    "falcon_monitor.service"
  ]
}
3. Service InstallationTo ensure the monitor runs reliably in the background, you must install it as a systemd service.A. Edit the Service File:Open the falcon_monitor.service file. You must change the WorkingDirectory and ExecStart lines to use the absolute path to your project directory and script.Example falcon_monitor.service:[Unit]
Description=Falcon Health Monitor Service
After=network-online.target

[Service]
User=root
# !!! CHANGE THIS PATH !!!
WorkingDirectory=/home/jetson/falcon_monitor/
# !!! CHANGE THIS PATH !!!
ExecStart=/usr/bin/python3 /home/jetson/falcon_monitor/falcon_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
B. Install and Start the Service:Run the following commands in your terminal:# Copy the service file to the systemd directory
sudo cp falcon_monitor.service /etc/systemd/system/falcon_monitor.service

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start automatically on boot
sudo systemctl enable falcon_monitor.service

# Start the service now
sudo systemctl start falcon_monitor.service
UsageThe monitor will now run in the background and log data every 10 minutes.Managing the ServiceCheck Status: sudo systemctl status falcon_monitor.serviceView Real-Time Logs: sudo journalctl -u falcon_monitor.service -fStop the Service: sudo systemctl stop falcon_monitor.serviceRestart the Service: sudo systemctl restart falcon_monitor.serviceQuerying the DatabaseAll historical data is stored in the health_monitor.db file. You can query it from the command line.1. Install the SQLite tool (if you don't have it):sudo apt-get install -y sqlite3
2. Query the data:# Open the database
sqlite3 health_monitor.db

# --- Inside the sqlite> prompt ---

# Improve formatting
.headers on
.mode column

# View the 5 most recent records
SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5;

# Exit the tool
.exit
Developed ByRajesh RoyCTO at Assert AI and NVIDIA SpecialistEmail: rajeshroy402@gmail.comLinkedIn: www.linkedin.com/in/rajeshroy402
