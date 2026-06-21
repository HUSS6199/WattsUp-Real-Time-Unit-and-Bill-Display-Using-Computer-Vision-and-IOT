# Raspberry Pi 4 & Camera V3 Setup Guide

## Hardware Requirements
- **Raspberry Pi 4** (4GB RAM minimum, 8GB recommended)
- **Pi Camera V3** (12MP with autofocus)
- **Power Supply** (5.1V/3A or better)
- **MicroSD Card** (32GB+ class 10)
- **USB-C to USB-A adapter** (for Pi 4)
- **Ethernet cable** or stable Wi-Fi

## Initial Setup

### 1. Flash Raspberry Pi OS
```bash
# Download Raspberry Pi Imager from https://www.raspberrypi.com/software/
# Choose: Raspberry Pi OS (64-bit) - Lite or Desktop
# Flash to microSD card
```

### 2. Boot & Connect
- Insert microSD into Pi
- Connect power and ethernet/Wi-Fi
- Wait 1-2 minutes for first boot
- SSH into Pi: `ssh pi@raspberrypi.local`

### 3. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 4. Enable Camera Interface
```bash
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
# Reboot after enabling
```

### 5. Install Pi Camera V3 Drivers
```bash
sudo apt install -y libcamera-tools
# Test camera: libcamera-still -t 1000 -o test.jpg
```

## Install WattsUp Dependencies

### 1. Install Python & pip
```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Clone WattsUp Repository
```bash
git clone https://github.com/HUSS6199/WattsUp-Real-Time-Unit-and-Bill-Display-Using-Computer-Vision-and-IOT.git
cd WattsUp-Real-Time-Unit-and-Bill-Display-Using-Computer-Vision-and-IOT
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Additional system dependencies for OpenCV
sudo apt install -y libatlas-base-dev libjasper-dev libharfbuzz0b libwebp6 libtiff5 libjasper1 libopenjp2-7 libtiffxx5
```

### 5. Install Tesseract OCR
```bash
sudo apt install -y tesseract-ocr libtesseract-dev
```

## Firebase Configuration

### 1. Create Firebase Project
- Go to [Firebase Console](https://console.firebase.google.com/)
- Create new project named "WattsUp"
- Enable Realtime Database

### 2. Generate Service Account Key
- In Firebase Console → Project Settings → Service Accounts
- Click "Generate New Private Key"
- Save as `serviceAccountKey.json`
- **KEEP THIS FILE SECRET**

### 3. Copy to Pi
```bash
scp serviceAccountKey.json pi@raspberrypi.local:~/WattsUp/scripts/
```

## Camera Positioning

### Physical Setup
1. **Mount height**: Position camera at eye level with meter display
2. **Distance**: 15-30cm from meter face (adjust for focus)
3. **Angle**: Point directly at display (perpendicular to screen)
4. **Lighting**: Ensure adequate ambient light, avoid shadows

### Focus Calibration (Pi Camera V3)
```bash
# Take test image and focus
rpicam-still -t 3000 --autofocus-mode continuous -o focus_test.jpg
```

## Run WattsUp Monitoring

### Manual Execution
```bash
cd ~/WattsUp
source venv/bin/activate
python3 scripts/main.py
```

### Auto-Start on Boot (Crontab)
```bash
crontab -e

# Add this line (runs at boot):
@reboot sleep 30 && cd /home/pi/WattsUp && source venv/bin/activate && python3 scripts/main.py >> /var/log/wattsup.log 2>&1
```

### Create SystemD Service (Alternative)
```bash
sudo nano /etc/systemd/system/wattsup.service
```

Add:
```ini
[Unit]
Description=WattsUp Meter Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/WattsUp
ExecStart=/home/pi/WattsUp/venv/bin/python3 scripts/main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/wattsup.log
StandardError=append:/var/log/wattsup.log

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable wattsup
sudo systemctl start wattsup

# Check status:
sudo systemctl status wattsup
sudo tail -f /var/log/wattsup.log
```

## Troubleshooting

### Camera Not Detected
```bash
# Check camera connection
vcsm_pcie_status

# List cameras
libcamera-hello --list-cameras

# Test capture
rpicam-still -t 2000 -o test.jpg
```

### Firebase Connection Issues
```bash
# Test connectivity
ping 8.8.8.8
wifi-status  # or check ethernet

# Verify Firebase URL is correct in main.py
```

### Slow Inference Speed
- Reduce image resolution in `main.py` (1280x960 → 1024x768)
- Increase `CAPTURE_INTERVAL` for longer waits between captures
- Consider GPU acceleration (not available on Pi 4, requires external hardware)

### High CPU Usage
```bash
# Monitor performance
top
# or
watch -n 1 vcgencmd measure_temp
```

## Performance Optimization

### Reduce Power Consumption
```bash
# Disable HDMI if not needed
tvservice -o

# Reduce clock speed (if overheating)
sudo nano /boot/firmware/config.txt
# Add: arm_freq=1500
```

### Network Optimization
- Use ethernet for stable connection (recommended)
- Set static IP if using Wi-Fi
- Monitor signal strength: `iwconfig`

## Useful Commands

```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Monitor system logs
sudo journalctl -u wattsup -f

# View temperature
vcgencmd measure_temp

# Check CPU throttling
vcgencmd get_throttled
```

## Security Best Practices

1. **Change default password**
   ```bash
   passwd
   ```

2. **Configure SSH key-based auth**
   ```bash
   ssh-keygen -t rsa -b 4096
   # Add public key to ~/.ssh/authorized_keys
   ```

3. **Keep serviceAccountKey.json private**
   - Never commit to GitHub
   - Use `.gitignore` to prevent accidental upload
   - Set file permissions: `chmod 600 serviceAccountKey.json`

4. **Enable firewall (if needed)**
   ```bash
   sudo apt install -y ufw
   sudo ufw enable
   sudo ufw allow ssh
   ```
