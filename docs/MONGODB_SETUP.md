# MongoDB Atlas Setup Guide

This guide explains how to set up MongoDB Atlas for cloud deployment while keeping JSON fallback for local development.

## 🏗️ Architecture Overview

- **Local Development**: Uses JSON files (`scheduled_products.json`)
- **Cloud Production**: Uses MongoDB Atlas (free tier)
- **Automatic Fallback**: App gracefully handles both scenarios

## 🌍 MongoDB Atlas Setup (Free Tier)

### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click "Try Free" and create an account
3. Choose "Build a Database" → "M0 Sandbox" (Free Forever)

### Step 2: Configure Database
1. **Cloud Provider**: Choose AWS, Google Cloud, or Azure
2. **Region**: Select closest to your deployment region
3. **Cluster Name**: `product-tracker-cluster`
4. Click "Create Cluster"

### Step 3: Set Up Database User
1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. **Authentication Method**: Password
4. **Username**: `product_tracker_user`
5. **Password**: Generate secure password (save it!)  5Sageywemmbfa0ms
6. **Database User Privileges**: "Read and write to any database"
7. Click "Add User"

### Step 4: Configure Network Access
1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. **For Render deployment**: Select "Allow Access from Anywhere" (0.0.0.0/0)
4. **For security**: You can restrict to specific IPs later
5. Click "Confirm"

### Step 5: Get Connection String
1. Go to "Database" → "Connect"
2. Choose "Connect your application"
3. **Driver**: Python, Version 3.12 or later
4. Copy the connection string (looks like):
   ```
   mongodb+srv://product_tracker_user:<password>@product-tracker-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

mongodb+srv://product_tracker_user:<db_password>@product-tracker-cluster.aenuves.mongodb.net/?retryWrites=true&w=majority&appName=product-tracker-cluster


## 🔧 Environment Configuration

### Local Development (.env file)
```env
# Local uses JSON fallback (current setup)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=product_tracker
ENVIRONMENT=development
```

### Cloud Production (Render Environment Variables)
```env
# Set these in Render dashboard
MONGODB_URI=mongodb+srv://product_tracker_user:YOUR_PASSWORD@product-tracker-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=product_tracker
ENVIRONMENT=production
```

## 🚀 Deployment Steps

### 1. Update Render Environment Variables
In your Render dashboard:
1. Go to your service settings
2. Add environment variables:
   - `MONGODB_URI`: (your Atlas connection string)
   - `MONGODB_DATABASE`: `product_tracker`
   - `ENVIRONMENT`: `production`

### 2. Deploy to Render
```bash
git push origin develop
# Then merge to main when ready
```

### 3. Verify Connection
1. Check `/debug/database` endpoint
2. Should show `"connected": true` in production
3. Should show `"connected": false` locally (using JSON)

## 🔍 Database Status Monitoring

The app provides real-time database status:

- **Debug Dashboard**: `/debug` - Shows connection status card
- **Database Details**: `/debug/database` - Full connection information
- **Logs**: Check application logs for connection messages

## 📊 Data Migration

The system automatically:
1. **Migrates JSON to MongoDB** on first connection
2. **Maintains JSON backup** for local development
3. **Syncs changes** between MongoDB and JSON fallback

## 🔒 Security Best Practices

### For Production:
- Use strong passwords for database users
- Restrict IP access after deployment
- Use environment variables (never commit credentials)
- Enable MongoDB Atlas monitoring

### For Development:
- Keep `.env` file in `.gitignore`
- Use different databases for dev/test/prod
- Regular backup of JSON files

## 🆘 Troubleshooting

### Connection Issues:
1. Check network access whitelist
2. Verify connection string format
3. Ensure user credentials are correct
4. Check application logs for specific errors

### Local Development:
- JSON fallback should work automatically
- No MongoDB installation required locally
- Check `scheduled_products.json` for data persistence

## 📈 Monitoring & Maintenance

- **MongoDB Atlas Dashboard**: Monitor usage, performance
- **Application Logs**: Connection status and errors
- **Debug Endpoints**: Real-time status information
- **Backup Strategy**: Atlas automatic backups + local JSON

---

## ✅ Ready for Deployment

Once MongoDB Atlas is configured, your application will:
- ✅ Use MongoDB in production (persistent across restarts)
- ✅ Use JSON locally (simple development)
- ✅ Handle connection failures gracefully
- ✅ Provide monitoring and debug information
