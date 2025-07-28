# Scheduler Logic Examples
# 
# This shows how the new cron-based scheduling works:

## Example 1: Start at 04:00, Every 12 hours
- Start Time: 04:00  
- Interval: 12 hours
- Run Times: 04:00, 16:00 (4 AM, 4 PM daily)
- Cron Pattern: hour='4,16', minute=0

## Example 2: Start at 08:00, Every 6 hours  
- Start Time: 08:00
- Interval: 6 hours
- Run Times: 08:00, 14:00, 20:00, 02:00 (8 AM, 2 PM, 8 PM, 2 AM daily)
- Cron Pattern: hour='8,14,20,2', minute=0

## Example 3: Start at 09:00, Every 24 hours
- Start Time: 09:00
- Interval: 24 hours  
- Run Times: 09:00 (9 AM daily)
- Cron Pattern: hour=9, minute=0

## Example 4: Start at 00:00, Every 4 hours
- Start Time: 00:00
- Interval: 4 hours
- Run Times: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 (Every 4 hours starting midnight)
- Cron Pattern: hour='0,4,8,12,16,20', minute=0

# Key Benefits:
# 1. Jobs ALWAYS run at consistent times based on start_time
# 2. No drift - if you set 9 AM, it will ALWAYS be 9 AM (not 9:01, 9:02, etc.)
# 3. Predictable scheduling - you know exactly when jobs will run
# 4. Proper interval patterns - 6-hour intervals from 8 AM = 8 AM, 2 PM, 8 PM, 2 AM
