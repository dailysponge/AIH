<div align="center">
  <h1>🌿 Nature Connect Bot</h1>
  <p>Connecting urban dwellers with nature through personalized AI interactions</p>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Platform-Telegram-blue?style=for-the-badge&logo=telegram" alt="Telegram">
  <img src="https://img.shields.io/badge/Made%20with-Python-green?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/AI-Gemini%20Pro-orange?style=for-the-badge&logo=google" alt="Gemini">
</div>

<div>
  <h2>📖 About</h2>
  <p>Nature Connect Bot is an innovative Telegram chatbot designed to encourage people in Singapore to connect with nature through personalized activities and social interactions. The bot uses advanced AI to understand users' personalities and preferences, suggesting nature-related activities while considering real-time weather conditions.</p>
</div>

<div>
  <h2>🔧 Setup Instructions</h2>
  
  <h3>Prerequisites</h3>
  <ul>
    <li>Python 3.8 or higher</li>
    <li>Telegram account</li>
    <li>Google Cloud account</li>
    <li>ngrok account</li>
  </ul>

  <h3>1. Clone the Repository</h3>
  
  ```bash
  git clone https://github.com/dailysponge/AIH.git
  ```

  <h3>2. Install Dependencies</h3>
  
  ```bash
  pip install -r requirements.txt
  ```

  <h3>3. Set Up Environment Variables</h3>
  Create a .env file in the root directory:
  
  ```bash
  # Telegram Bot Token (from @BotFather)
  TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# WeatherAPI Key (from weatherapi.com)

WEATHERAPI_KEY=your_weather_api_key

# Google Cloud Project ID

GOOGLE_CLOUD_PROJECT=your_project_id

# Google Custom Search Engine ID, obtain from https://programmablesearchengine.google.com/u/7/controlpanel/all

GOOGLE_CSE_ID=your_search_engine_id

# Google API Key, obtain from https://developers.google.com/custom-search/v1/overview

GOOGLE_API_KEY=your_google_api_key

# Webhook URL (from ngrok)

WEBHOOK_URL=your_ngrok_url

````

<h3>4. Set Up External Services</h3>
<ol>
  <li><b>Telegram Bot:</b>
    <ul>
      <li>Create a new bot with @BotFather on Telegram</li>
      <li>Save the bot token in your .env file</li>
    </ul>
  </li>
  <li><b>Weather API:</b>
    <ul>
      <li>Sign up at weatherapi.com</li>
      <li>Generate an API key</li>
      <li>Add the key to your .env file</li>
    </ul>
  </li>
  <li><b>Google Cloud:</b>
    <ul>
      <li>Create a new project in Google Cloud Console</li>
      <li>Enable Vertex AI API</li>
      <li>Create service account credentials</li>
      <li>Download the JSON key file</li>
      <li>Set up Custom Search Engine and get the CSE ID</li>
    </ul>
  </li>
  <li><b>ngrok:</b>
    <ul>
      <li>Install ngrok</li>
      <li>Start ngrok: <code>ngrok http 8000</code></li>
      <li>Copy the HTTPS URL to your .env file</li>
    </ul>
  </li>
</ol>

<h3>5. Initialize Google Cloud</h3>

```
# Set Google Cloud credentials
````

  <h3>6. Run the Bot</h3>
  ```
  python -m app
  ```

  <h3>7. Verify Setup</h3>
  <ul>
    <li>Open Telegram and search for your bot</li>
    <li>Start a conversation with /start command</li>
    <li>The bot should respond with a personality selection menu</li>
  </ul>
</div>

<div>
  <h2>✨ Key Features</h2>
  
  <h3>🎭 Personality-Based Interaction</h3>
  <ul>
    <li>Users take a personality quiz to identify their nature interaction style</li>
    <li>Six unique personality types:
      <ul>
        <li>🏃‍♂️ <b>Adventurous Andy:</b> For thrill-seekers and outdoor enthusiasts</li>
        <li>🎯 <b>Spontaneous Sammy:</b> For flexible, go-with-the-flow nature lovers</li>
        <li>🌍 <b>Planet Pete:</b> For environmentally conscious individuals</li>
        <li>😌 <b>Chill Charlie:</b> For those seeking peaceful nature experiences</li>
        <li>🎮 <b>Gamer George:</b> For those who enjoy gamified outdoor activities</li>
        <li>📱 <b>Trendy Tiara:</b> For social media enthusiasts seeking Instagram-worthy nature spots</li>
      </ul>
    </li>
  </ul>

  <h3>🌦️ Smart Activity Suggestions</h3>
  <ul>
    <li>Real-time weather integration for contextual recommendations</li>
    <li>Considers temperature, precipitation, and time of day</li>
    <li>Personalizes suggestions based on user's personality type</li>
    <li>Provides Singapore-specific nature activities and locations</li>
  </ul>

  <h3>🏆 Gamification Elements</h3>
  <ul>
    <li>Point system to encourage participation:
      <ul>
        <li>20 points for completing nature activities</li>
        <li>10 points for adding friends</li>
        <li>5 points for sharing nature photos</li>
        <li>10 points for providing feedback</li>
      </ul>
    </li>
    <li>Leaderboard to track and compare progress with friends</li>
    <li>Social features to share achievements</li>
  </ul>

  <h3>📸 Image Recognition</h3>
  <ul>
    <li>Users can share photos of nature</li>
    <li>AI-powered image analysis provides interesting facts and context</li>
    <li>Points awarded for sharing nature discoveries</li>
  </ul>

  <h3>👥 Social Features</h3>
  <ul>
    <li>Add friends to create a nature-loving community</li>
    <li>Automatic notifications when friends complete activities</li>
    <li>Encourages group participation and friendly competition</li>
  </ul>
</div>

<div>
  <h2>🛠️ Technical Implementation</h2>
  <p>The bot leverages several advanced technologies:</p>
  <ul>
    <li>AI-powered conversation using Google's Gemini model</li>
    <li>Real-time weather data integration</li>
    <li>Image recognition capabilities</li>
    <li>Secure user data management</li>
    <li>Webhook-based message handling</li>
  </ul>
</div>

<div>
  <h2>🎯 Design Philosophy</h2>
  <p>The project follows key principles:</p>
  <ol>
    <li><b>Accessibility:</b> Easy to use through Telegram's familiar interface</li>
    <li><b>Personalization:</b> Adapts to individual preferences and personalities</li>
    <li><b>Engagement:</b> Gamification elements maintain user interest</li>
    <li><b>Community:</b> Social features encourage group participation</li>
    <li><b>Education:</b> Subtle learning about local nature spots and environmental awareness</li>
  </ol>
</div>

<div>
  <h2>💫 Impact</h2>
  <p>Nature Connect Bot aims to:</p>
  <ul>
    <li>Increase nature engagement in urban Singapore</li>
    <li>Build communities around nature activities</li>
    <li>Promote environmental awareness</li>
    <li>Improve mental well-being through nature connection</li>
    <li>Make nature activities more accessible and enjoyable</li>
  </ul>
</div>

<div>
  <h2>🚀 Future Developments</h2>
  <p>Planned enhancements include:</p>
  <ul>
    <li>Group activity coordination</li>
    <li>Seasonal challenges and events</li>
    <li>Environmental impact tracking</li>
    <li>Integration with local nature organizations</li>
    <li>Enhanced social features and group interactions</li>
  </ul>
</div>

<div align="center">
  <p><i>This project represents a unique blend of technology and nature, designed to help urban dwellers reconnect with the natural world in a fun and engaging way.</i></p>
</div>

<div align="center">
  <h2>📱 Try it Now</h2>
  <p>Start your nature journey today: <a href="https://t.me/EcoBuddy_bot">@EcoBuddy_bot</a></p>
</div>
