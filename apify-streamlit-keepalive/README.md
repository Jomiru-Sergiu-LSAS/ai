# Streamlit Keepalive Monitor

An Apify Actor that keeps your Streamlit app awake by pinging it at regular intervals, preventing it from going to sleep due to inactivity.

## Features

- Automatically pings your Streamlit app at configurable intervals
- Monitors uptime and response times
- Logs all ping attempts with timestamps and status
- Tracks success/failure statistics
- Can run continuously or for a specified duration
- Configurable timeout and retry logic

## Use Cases

- Keep free-tier Streamlit apps active
- Monitor app availability
- Prevent cold starts
- Ensure your app is always responsive

## Configuration

### Input Parameters

- **Streamlit App URL** (required): The URL of your Streamlit app
  - Default: `https://lsas-terminal.streamlit.app/`

- **Ping Interval** (optional): How often to ping the app in minutes
  - Default: `5` minutes
  - Range: 1-60 minutes
  - Recommended: 5-10 minutes for optimal keepalive

- **Maximum Pings** (optional): Total number of pings before stopping
  - Default: `6` (30 minutes with 5-minute intervals - free tier friendly)
  - For paid tier: Use 144+ for longer monitoring periods

- **Request Timeout** (optional): Maximum wait time for response in milliseconds
  - Default: `30000` (30 seconds)
  - Range: 5000-120000 ms

- **User Agent** (optional): Custom User-Agent header
  - Default: `Apify-Keepalive-Bot/1.0`

## Setup Instructions

### Option 1: Deploy to Apify Console

1. Go to [Apify Console](https://console.apify.com/)
2. Click **Actors** > **Create new**
3. Choose **Empty Actor**
4. Copy all files from this repository to your actor
5. Click **Build** to build the actor
6. Once built, click **Start** to run it

### Option 2: Use Apify CLI

1. Install Apify CLI:
   ```bash
   npm install -g apify-cli
   ```

2. Login to Apify:
   ```bash
   apify login
   ```

3. Navigate to the actor directory:
   ```bash
   cd apify-streamlit-keepalive
   ```

4. Push to Apify:
   ```bash
   apify push
   ```

5. Run the actor:
   ```bash
   apify call
   ```

## Scheduling

To keep your Streamlit app permanently awake, set up a scheduled run:

### Important: Timeout Configuration

**Before running**, configure the timeout to avoid premature termination:

1. Click **"Advanced configuration"** or the gear icon ⚙️
2. Set **"Timeout"** based on your configuration:
   - Free tier: `3600` seconds (1 hour) - run hourly
   - Paid tier: `86400` seconds (24 hours) - run daily

### Free Tier Schedule (Recommended for most users)

1. In Apify Console, go to your actor
2. Click **Schedule** tab
3. Create a new schedule:
   - **Frequency**: Every 1 hour
   - **Timeout**: 3600 seconds (1 hour)
   - **Input**:
     ```json
     {
       "intervalMinutes": 5,
       "maxPings": 6
     }
     ```

This runs for ~30 minutes every hour, pinging every 5 minutes (6 pings total per run).

### Paid Tier Schedule (For continuous 24/7 monitoring)

- **Frequency**: Every 24 hours
- **Timeout**: 86400 seconds (24 hours)
- **Input**:
  ```json
  {
    "intervalMinutes": 10,
    "maxPings": 144
  }
  ```

This ensures your app is pinged every 10 minutes, 24/7.

## Output

The actor stores results in two formats:

### 1. Dataset (Per-Ping Results)
Each ping attempt is logged with:
- `timestamp`: When the ping occurred
- `pingNumber`: Sequential ping number
- `status`: "success" or "failure"
- `statusCode`: HTTP response code (if successful)
- `responseTime`: Time taken in milliseconds
- `error`: Error message (if failed)
- `url`: The pinged URL

### 2. Key-Value Store (Statistics)
Overall statistics stored in `statistics` key:
- `totalPings`: Total number of pings attempted
- `successCount`: Number of successful pings
- `failureCount`: Number of failed pings
- `successRate`: Percentage of successful pings
- `lastUpdate`: Last update timestamp
- `url`: The monitored URL

## Example Usage

### Free Tier - Hourly Schedule (Recommended)
```json
{
  "streamlitUrl": "https://lsas-terminal.streamlit.app/",
  "intervalMinutes": 5,
  "maxPings": 6
}
```
Schedule: Every 1 hour with 1-hour timeout

### Paid Tier - Daily Schedule (24/7 monitoring)
```json
{
  "streamlitUrl": "https://lsas-terminal.streamlit.app/",
  "intervalMinutes": 10,
  "maxPings": 144
}
```
Schedule: Every 24 hours with 24-hour timeout

### Custom - 2 Hour Monitoring Window
```json
{
  "streamlitUrl": "https://lsas-terminal.streamlit.app/",
  "intervalMinutes": 5,
  "maxPings": 24
}
```
Schedule: Every 2 hours with 2-hour timeout

## Cost Estimation

Apify charges based on compute units. This actor is very lightweight:
- ~1 compute unit per 24 hours of operation (with 10-minute intervals)
- Apify free tier includes $5 of free usage per month
- Perfect for keeping 1-2 Streamlit apps awake 24/7 for free

## Monitoring

View your actor runs in the Apify Console:
1. Go to **Storage** > **Datasets** to see all ping results
2. Check **Key-Value Store** for overall statistics
3. View **Log** for real-time console output

## Troubleshooting

**Actor timing out after 5-6 minutes?**
- This is the default Apify timeout (300 seconds)
- **Solution**: Click "Advanced configuration" ⚙️ before running
- Set timeout to match your run duration:
  - 30 min run = 3600 seconds
  - 1 hour run = 3600 seconds
  - 24 hour run = 86400 seconds

**App still going to sleep?**
- Reduce `intervalMinutes` to 5 minutes
- Increase schedule frequency (run every hour instead of every 24 hours)
- Check the dataset for any failed pings

**Too many failed pings?**
- Increase `timeout` value in input parameters
- Check if your Streamlit app URL is correct
- Verify your app is publicly accessible
- Some Streamlit apps return 303 redirects (this is normal and counts as success)

## License

MIT

## Support

For issues or questions:
- Check the Apify documentation: https://docs.apify.com/
- Review Streamlit docs: https://docs.streamlit.io/
