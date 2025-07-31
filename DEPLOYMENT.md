# N2S Impact Model - Deployment Guide

This guide will help you deploy the N2S Impact Model Streamlit application to your server at motoko.hopto.org.

## Prerequisites

- SSH access to motoko.hopto.org on port 2222
- Domain name (motoko.hopto.org) pointing to your server
- Server running Ubuntu/Debian Linux
- Sudo privileges on the server

## Quick Deployment

### Step 1: Prepare the Server (Run once)

First, SSH into your server and prepare it:

```bash
ssh -p 2222 your-username@motoko.hopto.org
```

Then run the server setup script on the server:

```bash
# Download and run server setup
curl -sSL https://raw.githubusercontent.com/your-repo/n2s-impact-model/main/server-setup.sh | bash
```

Or copy the `server-setup.sh` script to your server and run:

```bash
chmod +x server-setup.sh
./server-setup.sh
```

### Step 2: Deploy the Application

From your local machine (in the project directory), run:

```bash
./deploy.sh
```

This script will:
- Copy all application files to the server
- Set up a Python virtual environment
- Install dependencies
- Create a systemd service for the app
- Configure Nginx as a reverse proxy
- Start the application

### Step 3: Access Your Application

Your app will be available at:
- **Primary URL**: http://motoko.hopto.org
- **Direct Streamlit**: http://motoko.hopto.org:8501

## Optional: Enable HTTPS

To enable SSL/HTTPS with Let's Encrypt (recommended for production):

1. SSH into your server
2. Edit the email in `ssl-setup.sh`
3. Run the SSL setup script:

```bash
./ssl-setup.sh
```

After SSL setup, your app will be available at: https://motoko.hopto.org

## Management Commands

### Check Application Status

```bash
ssh -p 2222 your-username@motoko.hopto.org 'sudo systemctl status n2s-impact-model'
```

### View Application Logs

```bash
ssh -p 2222 your-username@motoko.hopto.org 'sudo journalctl -f -u n2s-impact-model'
```

### Restart Application

```bash
ssh -p 2222 your-username@motoko.hopto.org 'sudo systemctl restart n2s-impact-model'
```

### Update Application

Simply run the deployment script again:

```bash
./deploy.sh
```

## Troubleshooting

### Application Won't Start

1. Check the service status:
   ```bash
   sudo systemctl status n2s-impact-model
   ```

2. Check the logs:
   ```bash
   sudo journalctl -u n2s-impact-model -n 50
   ```

3. Verify Python dependencies:
   ```bash
   cd /home/your-username/n2s-impact-model
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Nginx Issues

1. Test Nginx configuration:
   ```bash
   sudo nginx -t
   ```

2. Check Nginx status:
   ```bash
   sudo systemctl status nginx
   ```

3. Restart Nginx:
   ```bash
   sudo systemctl restart nginx
   ```

### Port Issues

Make sure these ports are open on your server:
- Port 80 (HTTP)
- Port 443 (HTTPS, if using SSL)
- Port 2222 (SSH)

### File Permissions

If you encounter permission issues:

```bash
# Fix ownership of app directory
sudo chown -R your-username:your-username /home/your-username/n2s-impact-model

# Fix service permissions
sudo chmod 644 /etc/systemd/system/n2s-impact-model.service
```

## Configuration

### Streamlit Configuration

The app uses configuration from `.streamlit/config.toml`:
- Runs on port 8501
- Configured for production (headless mode)
- Security settings enabled

### Service Configuration

The systemd service is configured to:
- Start automatically on boot
- Restart on failure
- Run as your user account
- Log to systemd journal

## File Structure on Server

```
/home/your-username/n2s-impact-model/
├── app.py                 # Main Streamlit app
├── model.py              # Core calculation engine
├── config.py             # Configuration and constants
├── requirements.txt      # Python dependencies
├── venv/                 # Python virtual environment
├── data/                 # Data files
├── .streamlit/
│   └── config.toml      # Streamlit configuration
└── ...                   # Other application files
```

## Security Considerations

1. **Firewall**: The setup script configures UFW to allow only necessary ports
2. **SSL/TLS**: Use the SSL setup script for HTTPS in production
3. **Updates**: Regularly update the server and application dependencies
4. **Backups**: Consider backing up the application data and configuration

## Performance Optimization

For high-traffic scenarios, consider:

1. **Resource Monitoring**: Monitor CPU and memory usage
2. **Caching**: Streamlit has built-in caching for data operations
3. **Load Balancing**: Use multiple server instances behind a load balancer
4. **CDN**: Use a CDN for static assets if serving globally

## Support

For issues with deployment:
1. Check the troubleshooting section above
2. Review application logs
3. Verify server requirements are met
4. Check network connectivity and DNS resolution 