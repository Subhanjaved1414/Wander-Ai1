// Random Background Logic
const backgrounds = [
  "backgrounds/bg_1.jpg",
  "backgrounds/bg_2.jpg",
  "backgrounds/bg_3.jpg",
  "backgrounds/bg_4.jpg",
];

// Check if the element exists before trying to set the background
const heroImageHalf = document.querySelector('.hero-image-half');
// NOTE: The previous index.html uses #hero-background-image, not .hero-image-half.
// Preserving this original logic as requested, but adding a check.
if (heroImageHalf) {
  const randomBg = backgrounds[Math.floor(Math.random() * backgrounds.length)];
  heroImageHalf.style.backgroundImage = `url('${randomBg}')`;
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const targetElement = document.querySelector(this.getAttribute('href'));
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });
});

// Scroll-triggered header change (retaining this, as it's cleaner than CSS-only)
const header = document.querySelector('header');

window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});

// ==================== Recommendation Engine (Functionality retained) ====================
async function getRecommendation() {
  const budget = document.getElementById("budget").value;
  const season = document.getElementById("season").value;
  const dtype = document.getElementById("dtype").value;
  const interest = document.getElementById("interest").value;
  const climate = document.getElementById("weather").value;

  const resultDiv = document.getElementById("recommendation-result");
  if (!resultDiv) return; // Guard clause

  resultDiv.innerHTML = "<h3>Finding your perfect destination...</h3>";

  try {
    const response = await fetch("http://127.0.0.1:5000/recommend/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        budget: parseInt(budget),
        season,
        type: dtype, // Sends the correct key 'type'
        interest,
        climate
      })
    });

    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }

    const data = await response.json();

    if (data.length === 0 || data.recommendation || data.error) {
      // Handles case where Python returns an error/message object
      resultDiv.innerHTML = `<p>${data.recommendation || data.error || "No recommendations found. Try different filters."}</p>`;
    } else {
      resultDiv.innerHTML = data.map(
        (d, index) => `
              <div class="rec-card" style="animation-delay: ${0.2 * index}s;">
                <h3>${d.Destination}</h3>
                <p><strong>Country:</strong> ${d.Country}</p>
                <p><strong>Cost:</strong> $${d.Cost.toFixed(2)}</p> <p><strong>Season:</strong> ${d.Season}</p> <p><strong>Type:</strong> ${d.Type}</p>
              </div>
            `
      ).join("");
    }
  } catch (error) {
    console.error("Error fetching recommendation:", error);
    resultDiv.innerHTML = `<p>There was an error connecting to the server. Please ensure your backend is running. Error: ${error.message}</p>`;
  }
}

// ==================== Chatbot Logic (Functionality retained) ====================
async function sendMessage() {
  const userInputField = document.getElementById("user-input");
  const userInput = userInputField.value;
  if (!userInput) return;

  const chatBox = document.getElementById("chat-box");
  if (!chatBox) return; // Guard clause

  chatBox.innerHTML += `<div class="user-msg">You: ${userInput}</div>`;
  userInputField.value = "";

  // Add Typing Indicator
  const typingId = "typing-" + Date.now();
  chatBox.innerHTML += `
      <div class="bot-msg typing-indicator-container" id="${typingId}">
        <div class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;

  // Scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const response = await fetch("http://127.0.0.1:5000/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userInput })
    });

    const data = await response.json();

    // Remove typing indicator
    const typingElement = document.getElementById(typingId);
    if (typingElement) typingElement.remove();

    if (data.reply) {
      chatBox.innerHTML += `<div class="bot-msg">Bot: ${data.reply}</div>`;
    } else {
      chatBox.innerHTML += `<div class="bot-msg error">Error: ${data.error || "Unknown error"}</div>`;
    }
  } catch (err) {
    // Remove typing indicator on error
    const typingElement = document.getElementById(typingId);
    if (typingElement) typingElement.remove();

    chatBox.innerHTML += `<div class="bot-msg error">Error: Failed to connect to server.</div>`;
  }

}

// ==================== Weather Feature Logic ====================

window.showWeatherWidget = function () {
  const widget = document.getElementById('weather-widget');
  if (widget) {
    widget.style.display = 'flex';
    fetchWeather();
  }
};

window.hideWeatherWidget = function () {
  const widget = document.getElementById('weather-widget');
  if (widget) {
    widget.style.display = 'none';
  }
};

function fetchWeather() {
  const tempElement = document.getElementById('weather-temp');
  const descElement = document.getElementById('weather-desc');
  const locElement = document.getElementById('weather-location');
  const iconElement = document.getElementById('weather-icon');

  if (!navigator.geolocation) {
    locElement.innerHTML = '<i class="fas fa-map-marker-alt"></i> Location not supported';
    return;
  }

  navigator.geolocation.getCurrentPosition(async (position) => {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    try {
      // Fetch Weather from Open-Meteo
      const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;
      const weatherResponse = await fetch(weatherUrl);
      const weatherData = await weatherResponse.json();
      const current = weatherData.current_weather;

      // Update UI
      tempElement.innerText = `${Math.round(current.temperature)}°C`;
      descElement.innerText = getWeatherDescription(current.weathercode);
      iconElement.innerHTML = getWeatherIcon(current.weathercode);

      // Fetch City Name (Reverse Geocoding) - Using BigDataCloud Free API
      const cityUrl = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`;
      const cityResponse = await fetch(cityUrl);
      const cityData = await cityResponse.json();

      locElement.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${cityData.city || cityData.locality || "Unknown Location"}`;

    } catch (error) {
      console.error("Error fetching weather:", error);
      descElement.innerText = "Error loading data";
    }
  }, (error) => {
    console.error("Geolocation error:", error);
    locElement.innerHTML = '<i class="fas fa-map-marker-alt"></i> Location access denied';
  });
}

function getWeatherDescription(code) {
  // WMO Weather interpretation codes (WW)
  const codes = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail"
  };
  return codes[code] || "Unknown";
}

function getWeatherIcon(code) {
  // Mapping WMO codes to FontAwesome icons
  if (code === 0) return '<i class="fas fa-sun"></i>';
  if (code >= 1 && code <= 3) return '<i class="fas fa-cloud-sun"></i>';
  if (code === 45 || code === 48) return '<i class="fas fa-smog"></i>';
  if (code >= 51 && code <= 67) return '<i class="fas fa-cloud-rain"></i>';
  if (code >= 71 && code <= 77) return '<i class="fas fa-snowflake"></i>';
  if (code >= 80 && code <= 82) return '<i class="fas fa-cloud-showers-heavy"></i>';
  if (code >= 95) return '<i class="fas fa-bolt"></i>';
  return '<i class="fas fa-cloud"></i>';
}

// ==================== Atmosphere Animation Controller ====================
const AtmosphereController = {
  // Config
  states: ['weather-rain', 'weather-snow', 'weather-sunny', ''], // Empty string for clear/normal
  overlayId: 'weather-overlay',
  interval: 60000, // Change every 60 seconds (1 minute)

  // Initialize
  init: function () {
    this.createOverlay();
    this.startCycle();
    console.log("AtmosphereController Initialized");
  },

  // Create the overlay element if it doesn't exist
  createOverlay: function () {
    if (!document.getElementById(this.overlayId)) {
      const overlay = document.createElement('div');
      overlay.id = this.overlayId;
      overlay.className = 'weather-overlay'; // Base class
      document.body.appendChild(overlay);
    }
  },

  // Set specific weather
  setWeather: function (type) {
    const overlay = document.getElementById(this.overlayId);
    if (!overlay) return;

    // Remove all weather classes, keep base class
    overlay.className = 'weather-overlay';

    // Add new weather class if type is provided
    if (type) {
      // Force reflow to restart animation if needed (optional)
      void overlay.offsetWidth;
      overlay.classList.add(type);
    }
  },

  // Start the random cycle
  startCycle: function () {
    // Set initial random state immediately
    this.randomize();

    // Loop
    setInterval(() => {
      this.randomize();
    }, this.interval);
  },

  // Pick a random state
  randomize: function () {
    // Weighted random? Or just simple random
    const randIndex = Math.floor(Math.random() * this.states.length);
    const selectedWeather = this.states[randIndex];

    console.log(`AtmosphereController: Switching to ${selectedWeather || 'Clear'}`);
    this.setWeather(selectedWeather);
  }
};

// Start the controller when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  AtmosphereController.init();
});
