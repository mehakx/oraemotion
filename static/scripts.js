// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data to Make.com webhook
async function sendEmotionToMake(emotionData) {
    const makeWebhookUrl = "https://hook.eu2.make.com/mg0z2u8k9gv069uo14pj1exbil0a6q17";
    
    console.log('🚀 Attempting to send to Make.com webhook:', emotionData);
    
    // Create FLATTENED payload structure to match Make.com scenario
    const flattenedPayload = {
        user_id: chatId || 'anonymous',
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        primary_emotion: emotionData.emotion || 'neutral',
        confidence_score: Math.round((emotionData.confidence || 0) * 100), // Convert to percentage
        raw_text: emotionData.text || '',
        time_of_day: getTimeOfDay()
    };
    
    console.log('📦 Flattened payload:', flattenedPayload);
    
    try {
        // Try direct connection first with better error handling
        console.log('🔄 Attempting direct connection to Make.com...');
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(flattenedPayload),
            // Add timeout to prevent hanging
            signal: AbortSignal.timeout(10000) // 10 second timeout
        });
        
        console.log('📡 Direct response status:', directResponse.status);
        console.log('📡 Direct response ok:', directResponse.ok);
        console.log('📡 Direct response headers:', Object.fromEntries(directResponse.headers.entries()));
        
        if (directResponse.ok) {
            // Parse and handle the response from Make.com
            const responseText = await directResponse.text();
            console.log('✅ Direct response text:', responseText);
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
                console.log('✅ Direct Make.com webhook success (parsed JSON):', responseData);
            } catch (parseError) {
                console.log('⚠️ Response is not JSON, treating as text');
                responseData = { response: responseText, status: 'success' };
            }
            
            // Display the ORA response in the chat
            displayOraResponse(responseData);
            return true;
        } else {
            // Log the error response for debugging
            const errorText = await directResponse.text();
            console.error('❌ Direct connection failed with status:', directResponse.status);
            console.error('❌ Error response:', errorText);
            throw new Error(`HTTP ${directResponse.status}: ${errorText}`);
        }
        
    } catch (directError) {
        console.log('❌ Direct connection error details:');
        console.log('   Error type:', directError.constructor.name);
        console.log('   Error message:', directError.message);
        console.log('   Full error:', directError);
        
        // Better CORS detection
        if (directError.message.includes('CORS') || 
            directError.message.includes('cross-origin') ||
            directError.message.includes('Access-Control-Allow-Origin')) {
            console.log('🚫 Confirmed: This is a CORS error');
        } else if (directError.name === 'TypeError' && directError.message.includes('Failed to fetch')) {
            console.log('🚫 This looks like a CORS or network error (TypeError: Failed to fetch)');
        } else if (directError.name === 'AbortError') {
            console.log('⏰ Request timed out after 10 seconds');
        } else {
            console.log('🤔 This is a different type of error:', directError.name);
        }
        
        console.log('🔄 Trying CORS proxy as fallback...');
    }
    
    // Fallback to CORS proxy with better error handling
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const proxyUrl = corsProxyUrl + encodeURIComponent(makeWebhookUrl);
        console.log('🌐 Proxy URL:', proxyUrl);
        
        const response = await fetch(proxyUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(flattenedPayload),
            signal: AbortSignal.timeout(15000) // 15 second timeout for proxy
        });
        
        console.log('🌐 Proxy response status:', response.status);
        console.log('🌐 Proxy response ok:', response.ok);
        
        if (response.ok) {
            const responseText = await response.text();
            console.log('✅ Proxy response text:', responseText);
            
            // Handle the common "Oops... Request Timeout." from allorigins
            if (responseText.includes('Request Timeout') || responseText.includes('Oops')) {
                console.log('⚠️ Proxy service timed out or failed');
                throw new Error('Proxy service timeout');
            }
            
            try {
                // Try to parse the response as JSON
                const responseData = JSON.parse(responseText);
                console.log('✅ Parsed proxy response data:', responseData);
                displayOraResponse(responseData);
                return true;
            } catch (parseError) {
                console.log('⚠️ Proxy response not JSON, treating as text');
                // Even if parsing fails, display something
                displayOraResponse({response: responseText, status: 'success'});
                return true;
            }
        } else {
            const errorText = await response.text();
            console.error('❌ Proxy failed with status:', response.status, errorText);
            throw new Error(`Proxy error: ${response.status}`);
        }
        
    } catch (proxyError) {
        console.error('❌ Proxy method failed:');
        console.log('   Error type:', proxyError.constructor.name);
        console.log('   Error message:', proxyError.message);
        console.log('   Full error:', proxyError);
        
        // Try one more alternative method
        console.log('🔄 Trying alternative approach...');
        return await tryAlternativeMethod(flattenedPayload, makeWebhookUrl);
    }
}

// Alternative method: Use a different proxy or form submission
async function tryAlternativeMethod(payload, webhookUrl) {
    try {
        // Method 1: Try a different CORS proxy
        console.log('🔄 Trying cors-anywhere proxy...');
        const corsAnywhereUrl = 'https://cors-anywhere.herokuapp.com/';
        const response = await fetch(corsAnywhereUrl + webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload),
            signal: AbortSignal.timeout(10000)
        });
        
        if (response.ok) {
            const responseText = await response.text();
            console.log('✅ Alternative proxy success:', responseText);
            displayOraResponse({response: responseText, status: 'success'});
            return true;
        }
    } catch (altError) {
        console.log('❌ Alternative proxy also failed:', altError.message);
    }
    
    // Method 2: Try with FormData instead of JSON
    try {
        console.log('🔄 Trying FormData approach...');
        const formData = new FormData();
        Object.keys(payload).forEach(key => {
            formData.append(key, payload[key]);
        });
        
        const response = await fetch(webhookUrl, {
            method: 'POST',
            body: formData // No Content-Type header - let browser set it
        });
        
        if (response.ok) {
            const responseText = await response.text();
            console.log('✅ FormData approach success:', responseText);
            displayOraResponse({response: responseText, status: 'success'});
            return true;
        }
    } catch (formError) {
        console.log('❌ FormData approach failed:', formError.message);
    }
    
    // Final fallback: Show error to user
    console.error('❌ All connection methods failed');
    displayErrorMessage('Unable to connect to wellness agent. Please check your internet connection and try again.');
    return false;
}

// Helper function to display error messages
function displayErrorMessage(message) {
    const chatHistory = document.getElementById("chatHistory");
    if (chatHistory) {
        chatHistory.innerHTML += `<div class="assistant error">⚠️ ${message}</div>`;
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

// Helper function to get time of day
function getTimeOfDay() {
    const hour = new Date().getHours();
    if (hour < 6) return "night";
    if (hour < 12) return "morning";
    if (hour < 17) return "afternoon";
    if (hour < 22) return "evening";
    return "night";
}
