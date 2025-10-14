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

- **Ping Interval** (optional): Interval between pings within a single run
  - Default: `5` minutes
  - Only applies if maxPings > 1
  - For single-ping mode, use Apify scheduler to control frequency

- **Maximum Pings** (optional): Total number of pings per run before stopping
  - Default: `1` (recommended - single ping per run, scheduler handles repetition)
  - Set higher for multiple pings within one run (uses more compute time)

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

### Recommended: Single-Ping Mode (Most Efficient)

Each actor run does **one quick ping** (~1 second), then exits. The scheduler handles repetition.

1. In Apify Console, go to your actor
2. Click **Schedule** tab
3. Create a new schedule:
   - **Frequency**: Choose based on your needs:
     - **Every 5 minutes** - Most responsive (highly recommended)
     - **Every 10 minutes** - Good balance
     - **Every 30 minutes** - Minimal usage
   - **Timeout**: 60 seconds (default is fine)
   - **Input**: Leave empty or use:
     ```json
     {
       "maxPings": 1
     }
     ```

**Benefits:**
- ✅ No timeout issues (runs complete in ~1 second)
- ✅ Minimal compute usage
- ✅ Reliable scheduling
- ✅ Easy to adjust frequency

### Alternative: Multi-Ping Mode (For longer runs)

If you prefer fewer, longer-running scheduled tasks:

- **Frequency**: Every 1 hour
- **Timeout**: 3600 seconds (1 hour)
- **Input**:
  ```json
  {
    "intervalMinutes": 5,
    "maxPings": 6
  }
  ```

This pings 6 times over 30 minutes, once per hour.

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

### Single-Ping Mode (Recommended)
```json
{
  "streamlitUrl": "https://lsas-terminal.streamlit.app/",
  "maxPings": 1
}
```
**Schedule:** Every 5-10 minutes (no timeout issues)

### Multi-Ping Mode (Batch Processing)
```json
{
  "streamlitUrl": "https://lsas-terminal.streamlit.app/",
  "intervalMinutes": 5,
  "maxPings": 6
}
```
**Schedule:** Every 1 hour with 1-hour timeout (6 pings per run)

## Cost Estimation

Apify charges based on compute units. This actor is **extremely lightweight** in single-ping mode:

**Single-Ping Mode:**
- ~1 second per run
- Every 5 minutes = 288 runs/day
- **~0.1 compute units per day** (very minimal)
- Apify free tier includes $5 of free usage per month
- Can keep **10+ Streamlit apps** awake 24/7 within free tier

**Multi-Ping Mode:**
- Slightly higher usage based on run duration
- Still very cost-effective

## Monitoring

View your actor runs in the Apify Console:
1. Go to **Storage** > **Datasets** to see all ping results
2. Check **Key-Value Store** for overall statistics
3. View **Log** for real-time console output

## Troubleshooting

**Actor timing out?**
- **Solution**: Use single-ping mode (`maxPings: 1`)
- Each run completes in ~1 second (no timeout issues)
- Let Apify scheduler handle repetition instead

**App still going to sleep?**
- Increase schedule frequency to **every 5 minutes**
- Verify schedule is active and running
- Check the dataset for any failed pings

**Too many failed pings?**
- Increase `timeout` value in input parameters (default: 30 seconds)
- Check if your Streamlit app URL is correct
- Verify your app is publicly accessible
- Some Streamlit apps return 303 redirects (this is **normal** and counts as success)

**Want to test manually?**
- Use default settings (maxPings: 1)
- No need to adjust timeout
- Should complete in 1-2 seconds

## License

MIT

## Support

For issues or questions:
- Check the Apify documentation: https://docs.apify.com/
- Review Streamlit docs: https://docs.streamlit.io/
