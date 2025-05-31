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
        user_id: chatId,
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        primary_emotion: emotionData.emotion,
        confidence_score: emotionData.confidence,
        raw_text: emotionData.text,
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
            body: JSON.stringify(flattenedPayload)
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
        
        // Check if it's a CORS error specifically
        if (directError.message.includes('CORS') || directError.message.includes('cross-origin')) {
            console.log('🚫 Confirmed: This is a CORS error');
        } else if (directError.name === 'TypeError' && directError.message.includes('Failed to fetch')) {
            console.log('🚫 This looks like a CORS or network error');
        } else {
            console.log('🤔 This is a different type of error');
        }
        
        console.log('🔄 Trying CORS proxy as fallback...');
    }
    
    // Fallback to CORS proxy with better error handling
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const proxyUrl = corsProxyUrl + encodeURIComponent(makeWebhookUrl);
        console.log('🌐 Proxy URL:', proxyUrl);
        
        const response = await
