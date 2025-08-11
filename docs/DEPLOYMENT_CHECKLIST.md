# Cloud Deployment Checklist

## 📋 Pre-Deployment Checklist

### ✅ MongoDB Atlas Setup
- [ ] Create MongoDB Atlas account
- [ ] Create M0 Sandbox cluster (free tier)
- [ ] Create database user with read/write permissions
- [ ] Configure network access (allow 0.0.0.0/0 for Render)
- [ ] Get connection string
- [ ] Test connection locally (optional)

### ✅ Environment Variables Ready
- [ ] `TELEGRAM_BOT_TOKEN` - Your bot token
- [ ] `SECRET_KEY` - Generate secure key for Flask sessions
- [ ] `MONGODB_URI` - Atlas connection string
- [ ] `MONGODB_DATABASE` - Database name (product_tracker)
- [ ] `ENVIRONMENT` - Set to "production"

### ✅ Code Review
- [ ] All changes committed to develop branch
- [ ] Database module working with fallback
- [ ] Debug endpoints functional
- [ ] Requirements.txt updated with MongoDB deps
- [ ] No sensitive data in git repository

## 🚀 Deployment Steps

### Step 1: Merge to Main Branch
```bash
git checkout main
git merge develop
git push origin main
```

### Step 2: Configure Render Environment Variables
In Render dashboard → Environment:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
SECRET_KEY=your_secure_secret_key_here
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=product_tracker
ENVIRONMENT=production
```

### Step 3: Deploy and Monitor
- [ ] Deploy from main branch
- [ ] Check build logs for errors
- [ ] Verify application starts successfully
- [ ] Test `/debug/database` endpoint
- [ ] Confirm MongoDB connection established

### Step 4: Functional Testing
- [ ] Access main application (`/`)
- [ ] Add a test product via form
- [ ] Check debug dashboard (`/debug`)
- [ ] Verify scheduler is running
- [ ] Test manual product trigger
- [ ] Confirm data persists after restart

## 🔍 Post-Deployment Verification

### Database Status Check
Visit `/debug/database` should show:
```json
{
  "connected": true,
  "mongodb_uri": "mongodb+srv://...",
  "database": "product_tracker", 
  "environment": "production",
  "product_count": X
}
```

### Scheduler Status Check
Visit `/debug/scheduler` should show:
- Active jobs listed
- Next run times displayed
- Manual trigger buttons working

### Application Health Check
- [ ] Main page loads (`/`)
- [ ] Form submission works (`/form`)
- [ ] Tracking page displays data (`/tracking`)
- [ ] Chat management functional (`/chat`)
- [ ] Debug dashboard accessible (`/debug`)

## 🚨 Troubleshooting Guide

### MongoDB Connection Failed
- Check Atlas IP whitelist (should include 0.0.0.0/0)
- Verify connection string format
- Confirm database user credentials
- Check Atlas cluster status

### Application Won't Start
- Review Render build logs
- Check Python dependencies in requirements.txt
- Verify environment variables are set
- Look for import errors in logs

### Scheduler Not Working
- Check `/debug/scheduler` for job status
- Verify products are loaded from database
- Look for cron pattern errors in logs
- Test manual trigger functionality

### Data Not Persisting
- Confirm MongoDB connection is established
- Check if fallback to JSON is happening
- Verify database write permissions
- Monitor Atlas dashboard for activity

## 🎯 Success Criteria

✅ **Application Deployed Successfully**
- No build or runtime errors
- All pages accessible and functional
- Database connected to MongoDB Atlas

✅ **Data Persistence Working**
- Products survive container restarts
- New products saved to MongoDB
- Database status shows connected

✅ **Scheduler Operational** 
- Jobs scheduled according to configuration
- Manual triggers work correctly
- Next run times calculated properly

✅ **Monitoring Available**
- Debug dashboard provides system status
- Database connection can be verified
- Scheduler status is visible

## 📞 Support Resources

- **MongoDB Atlas**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **Render**: [render.com/docs](https://render.com/docs)
- **Application Logs**: Available in Render dashboard
- **Debug Endpoints**: `/debug`, `/debug/database`, `/debug/scheduler`

---

## 🎉 Ready for Production!

Once all checklist items are complete, your Product Cost Tracker will be:
- ✅ Running reliably on Render
- ✅ Storing data persistently in MongoDB Atlas  
- ✅ Scheduling jobs that survive restarts
- ✅ Providing comprehensive monitoring and debugging tools
