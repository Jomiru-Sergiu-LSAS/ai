import { Actor } from 'apify';

// Helper function for sleep
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Main Apify Actor entry point
await Actor.init();

try {
    // Get input from Apify console
    const input = await Actor.getInput();

    // Configuration with defaults
    const {
        streamlitUrl = 'https://lsas-terminal.streamlit.app/',
        intervalMinutes = 5,
        maxPings = 1, // Single ping per run - let scheduler handle repetition
        timeout = 30000, // 30 seconds
        userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    } = input || {};

    console.log(`Starting Streamlit keepalive monitor for: ${streamlitUrl}`);
    console.log(`Ping interval: ${intervalMinutes} minutes`);
    console.log(`Max pings: ${maxPings}`);

    let pingCount = 0;
    let successCount = 0;
    let failureCount = 0;

    // Main loop
    while (pingCount < maxPings) {
        pingCount++;
        const startTime = Date.now();

        try {
            console.log(`[${pingCount}/${maxPings}] Pinging ${streamlitUrl}...`);

            // Use fetch with AbortController for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            let response;
            try {
                response = await fetch(streamlitUrl, {
                    method: 'HEAD', // Use HEAD instead of GET for lighter requests
                    headers: {
                        'User-Agent': userAgent,
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive'
                    },
                    redirect: 'manual', // Don't follow redirects automatically
                    signal: controller.signal
                });
            } catch (fetchError) {
                // If HEAD fails, try GET as fallback
                console.log('HEAD request failed, trying GET...');
                response = await fetch(streamlitUrl, {
                    method: 'GET',
                    headers: {
                        'User-Agent': userAgent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive'
                    },
                    redirect: 'manual',
                    signal: controller.signal
                });
            }

            clearTimeout(timeoutId);

            const responseTime = Date.now() - startTime;

            // Consider any response that doesn't error as success
            // (including redirects, 404s, etc. - as long as server responds)
            successCount++;

            console.log(`✓ Success! Status: ${response.status}, Response time: ${responseTime}ms`);

            // Save ping result to dataset
            await Actor.pushData({
                timestamp: new Date().toISOString(),
                pingNumber: pingCount,
                status: 'success',
                statusCode: response.status,
                statusText: response.statusText,
                responseTime: responseTime,
                url: streamlitUrl,
                redirected: response.redirected,
                finalUrl: response.url
            });

        } catch (error) {
            const responseTime = Date.now() - startTime;
            failureCount++;

            const errorMessage = error.name === 'AbortError' ? 'Request timeout' : error.message;
            const errorDetails = {
                name: error.name,
                message: error.message,
                cause: error.cause?.message || error.cause || 'unknown',
                code: error.code || 'unknown'
            };

            console.error(`✗ Failed! Error: ${errorMessage}, Response time: ${responseTime}ms`);
            console.error('Error details:', JSON.stringify(errorDetails));

            // Save failure to dataset
            await Actor.pushData({
                timestamp: new Date().toISOString(),
                pingNumber: pingCount,
                status: 'failure',
                error: errorMessage,
                errorDetails: errorDetails,
                responseTime: responseTime,
                url: streamlitUrl
            });
        }

        // Update key-value store with current statistics
        await Actor.setValue('statistics', {
            totalPings: pingCount,
            successCount: successCount,
            failureCount: failureCount,
            successRate: ((successCount / pingCount) * 100).toFixed(2) + '%',
            lastUpdate: new Date().toISOString(),
            url: streamlitUrl
        });

        // Wait for the specified interval before next ping (unless it's the last ping)
        if (pingCount < maxPings) {
            const waitTime = intervalMinutes * 60 * 1000;
            console.log(`Waiting ${intervalMinutes} minutes until next ping...`);
            await sleep(waitTime);
        }
    }

    console.log('\n=== Final Statistics ===');
    console.log(`Total pings: ${pingCount}`);
    console.log(`Successful: ${successCount}`);
    console.log(`Failed: ${failureCount}`);
    console.log(`Success rate: ${((successCount / pingCount) * 100).toFixed(2)}%`);

} catch (error) {
    console.error('Actor failed with error:', error);
    throw error;
}

await Actor.exit();
