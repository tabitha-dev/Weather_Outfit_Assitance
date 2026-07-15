class WeatherOutfitApp {
  constructor() {
    this.currentCity = 'Redmond';
    this.currentWeather = null;
    this.preferences = {
      style: ['Casual', 'Minimalist'],
      clothingTypes: ['Jackets', 'Jeans', 'Sneakers'],
      colorPalette: ['Neutral', 'Blues']
    };
    this.favorites = [];
    
    this.loadPreferences();
    this.initializeElements();
    this.setupEventListeners();
    this.loadInitialData();
  }

  initializeElements() {
    // Search
    this.citySearch = document.getElementById('city-search');
    this.favoriteBtn = document.getElementById('favorite-btn');
    
    // Weather
    this.weatherCondition = document.getElementById('weather-condition');
    this.weatherTemp = document.getElementById('weather-temp');
    this.weatherFeelsLike = document.getElementById('weather-feels-like');
    this.weatherIcon = document.getElementById('weather-icon');
    
    // Preferences
    this.prefStyle = document.getElementById('pref-style');
    this.prefClothing = document.getElementById('pref-clothing');
    this.prefColors = document.getElementById('pref-colors');
    this.editPreferencesBtn = document.getElementById('edit-preferences-btn');
    
    // Outfit
    this.outfitItems = document.getElementById('outfit-items');
    this.thumbsUpBtn = document.getElementById('thumbs-up-btn');
    this.thumbsDownBtn = document.getElementById('thumbs-down-btn');
    
    // Chat
    this.chatMessages = document.getElementById('chat-messages');
    this.chatInput = document.getElementById('chat-input');
    this.sendBtn = document.getElementById('send-btn');
    
    // Header
    this.notificationsBtn = document.getElementById('notifications-btn');
    this.settingsBtn = document.getElementById('settings-btn');
  }

  setupEventListeners() {
    // City search
    this.citySearch.addEventListener('change', () => this.searchCity());
    this.citySearch.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.searchCity();
    });
    
    // Favorite button
    this.favoriteBtn.addEventListener('click', () => this.toggleFavorite());
    
    // Preferences
    this.editPreferencesBtn.addEventListener('click', () => this.editPreferences());
    
    // Feedback
    this.thumbsUpBtn.addEventListener('click', () => this.submitFeedback('positive'));
    this.thumbsDownBtn.addEventListener('click', () => this.submitFeedback('negative'));
    
    // Chat
    this.sendBtn.addEventListener('click', () => this.sendMessage());
    this.chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });
    
    // Quick actions
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const text = e.target.textContent.trim();
        this.handleQuickAction(text);
      });
    });
    
    // Header buttons
    this.notificationsBtn.addEventListener('click', () => this.showNotifications());
    this.settingsBtn.addEventListener('click', () => this.showSettings());
  }

  loadPreferences() {
    const saved = localStorage.getItem('outfitPreferences');
    if (saved) {
      this.preferences = JSON.parse(saved);
    }
    
    const savedFavorites = localStorage.getItem('favoriteCities');
    if (savedFavorites) {
      this.favorites = JSON.parse(savedFavorites);
    }
  }

  savePreferences() {
    localStorage.setItem('outfitPreferences', JSON.stringify(this.preferences));
    localStorage.setItem('favoriteCities', JSON.stringify(this.favorites));
  }

  updatePreferencesDisplay() {
    this.prefStyle.textContent = this.preferences.style.join(', ');
    this.prefClothing.textContent = this.preferences.clothingTypes.join(', ');
    this.prefColors.textContent = this.preferences.colorPalette.join(', ');
  }

  async loadInitialData() {
    this.updatePreferencesDisplay();
    this.updateFavoriteButton();
    await this.loadWeatherData();
    await this.loadOutfitSuggestions();
    
    // Add initial chat message
    this.addChatMessage('assistant', `Hi! Based on your preferences, here's a ${this.preferences.style[0].toLowerCase()} outfit for the ${this.currentWeather?.condition || 'current'} weather in ${this.currentCity}. Anything you'd like to change?`);
  }

  async searchCity() {
    const newCity = this.citySearch.value.trim();
    if (newCity && newCity !== this.currentCity) {
      this.currentCity = newCity;
      this.updateFavoriteButton();
      await this.loadWeatherData();
      await this.loadOutfitSuggestions();
      this.addChatMessage('assistant', `I've updated the outfit suggestions for ${this.currentCity}. How does this look?`);
    }
  }

  async loadWeatherData() {
    try {
      const response = await fetch(`/api/weather?city=${encodeURIComponent(this.currentCity)}`);
      const data = await response.json();
      
      this.currentWeather = {
        temperature: data.temperature,
        feelsLike: data.feels_like,
        condition: data.condition,
        city: data.city
      };
      
      this.updateWeatherDisplay();
      this.generateLocationQuickActions();  // Update quick actions based on location/weather
    } catch (error) {
      console.error('Failed to load weather:', error);
      this.addChatMessage('assistant', `Sorry, I couldn't fetch weather data for ${this.currentCity}. Using default suggestions.`);
    }
  }

  updateWeatherDisplay() {
    if (!this.currentWeather) return;
    
    const condition = this.currentWeather.condition.toLowerCase();
    
    console.log('🌤️ UPDATE WEATHER DISPLAY:', {
      city: this.currentCity,
      condition: condition,
      temp: this.currentWeather.temperature
    });
    
    this.weatherCondition.textContent = this.currentWeather.condition;
    this.weatherTemp.textContent = `${Math.round(this.currentWeather.temperature)}°F`;
    this.weatherFeelsLike.textContent = `Feels like ${Math.round(this.currentWeather.feelsLike)}°F`;
    
    // Update weather icon based on condition - check condition contains keyword
    let iconName = 'partly_cloudy_day';
    let colorClass = 'text-gray-400';
    
    if (condition.includes('clear') || condition.includes('sunny')) {
      iconName = 'wb_sunny';
      colorClass = 'text-amber-400';
    } else if (condition.includes('rain') || condition.includes('drizzle')) {
      iconName = 'rainy';
      colorClass = 'text-blue-500';
    } else if (condition.includes('snow')) {
      iconName = 'ac_unit';
      colorClass = 'text-cyan-300';
    } else if (condition.includes('storm') || condition.includes('thunder')) {
      iconName = 'thunderstorm';
      colorClass = 'text-purple-500';
    } else if (condition.includes('fog') || condition.includes('mist')) {
      iconName = 'foggy';
      colorClass = 'text-gray-500';
    } else if (condition.includes('overcast')) {
      iconName = 'cloud';
      colorClass = 'text-gray-500';
    } else if (condition.includes('partly') || condition.includes('partial')) {
      iconName = 'partly_cloudy_day';
      colorClass = 'text-gray-400';
    } else if (condition.includes('cloud')) {
      iconName = 'cloud';
      colorClass = 'text-gray-400';
    }
    
    console.log('🎨 ICON UPDATE:', {
      before: this.weatherIcon.className,
      iconName: iconName,
      colorClass: colorClass,
      matched: condition
    });
    
    // Apply icon and color
    this.weatherIcon.textContent = iconName;
    this.weatherIcon.className = `material-symbols-outlined text-7xl ${colorClass}`;
    
    console.log('✅ ICON APPLIED:', {
      after: this.weatherIcon.className,
      textContent: this.weatherIcon.textContent
    });
  }

  async loadOutfitSuggestions() {
    try {
      const params = new URLSearchParams({
        city: this.currentCity,
        temperature: this.currentWeather?.temperature || 65,
        condition: this.currentWeather?.condition || 'partly cloudy',
        style: this.preferences.style.join(','),
        types: this.preferences.clothingTypes.join(','),
        colors: this.preferences.colorPalette.join(',')
      });
      
      const response = await fetch(`/api/outfit?${params}`);
      const data = await response.json();
      
      this.renderOutfitItems(data.items);
    } catch (error) {
      console.error('Failed to load outfit:', error);
    }
  }

  renderOutfitItems(items) {
    this.outfitItems.innerHTML = '';
    
    const iconMap = {
      // Outerwear
      'outerwear': 'checkroom',
      'jacket': 'checkroom',
      'coat': 'checkroom',
      'overcoat': 'checkroom',
      'blazer': 'checkroom',
      'cardigan': 'checkroom',
      'windbreaker': 'air',
      
      // Formal Suits
      'suit': 'checkroom',
      'wool suit': 'checkroom',
      'lightweight suit': 'checkroom',
      'light-colored suit': 'checkroom',
      
      // Tops
      'top': 'checkroom',
      'shirt': 'checkroom',
      't-shirt': 'checkroom',
      'sweater': 'checkroom',
      'sleeveless': 'checkroom',
      'tank': 'checkroom',
      'athletic shirt': 'fitness_center',
      
      // Layers
      'layer': 'layers',
      'base layer': 'layers',
      'thermal': 'layers',
      
      // Bottoms
      'bottom': 'dry_cleaning',
      'jeans': 'dry_cleaning',
      'pants': 'dry_cleaning',
      'shorts': 'dry_cleaning',
      'skirt': 'checkroom',
      'snow pants': 'ac_unit',
      
      // Footwear
      'footwear': 'directions_walk',
      'sneakers': 'directions_walk',
      'shoes': 'directions_walk',
      'boots': 'hiking',
      'sandals': 'beach_access',
      'flip-flops': 'beach_access',
      'trail boots': 'hiking',
      'snow boots': 'ac_unit',
      
      // Weather Accessories
      'sunglasses': 'wb_sunny',
      'sun hat': 'wb_sunny',
      'umbrella': 'umbrella',
      'rain cover': 'umbrella',
      'waterproof': 'water_drop',
      
      // Cold Weather
      'hat': 'health_and_safety',
      'winter hat': 'health_and_safety',
      'warm hat': 'health_and_safety',
      'beanie': 'health_and_safety',
      'scarf': 'air',
      'gloves': 'back_hand',
      'face covering': 'masks',
      'goggles': 'visibility',
      
      // General Accessories
      'accessory': 'watch',
      'watch': 'watch',
      'bracelet': 'watch',
      'jewelry': 'diamond',
      'belt': 'straighten',
      'socks': 'checkroom',
      
      // Bags
      'bag': 'shopping_bag',
      'backpack': 'backpack',
      'tote': 'shopping_bag',
      'reservoir': 'water_drop',
      
      // Sports/Activity
      'visor': 'wb_sunny',
      'sweatband': 'fitness_center',
      'sports': 'sports_soccer',
      
      // Beach
      'swimwear': 'pool',
      'swim': 'pool',
      'cover-up': 'beach_access',
      'towel': 'beach_access',
      
      // Travel/Tech
      'pillow': 'hotel',
      'mask': 'masks',
      'toiletries': 'wash',
      'power bank': 'battery_charging_full',
      'documents': 'description',
      
      // Health/Safety
      'sunscreen': 'wb_sunny',
      'bug spray': 'pest_control',
      'lip balm': 'shopping_bag',
      'water bottle': 'water_drop',
      'snacks': 'fastfood',
      
      // Misc
      'cooling towel': 'ac_unit'
    };
    
    items.forEach(item => {
      const category = item.category.toLowerCase();
      const name = item.name.toLowerCase();
      
      // Find appropriate icon - prioritize name matches over category
      let icon = 'checkroom';
      
      // First try to match by name (more specific)
      let found = false;
      for (const [key, value] of Object.entries(iconMap)) {
        if (name.includes(key)) {
          icon = value;
          found = true;
          break;
        }
      }
      
      // If not found by name, try category
      if (!found) {
        for (const [key, value] of Object.entries(iconMap)) {
          if (category.includes(key)) {
            icon = value;
            break;
          }
        }
      }
      
      const itemEl = document.createElement('div');
      itemEl.className = 'flex flex-col gap-3 pb-3 rounded-xl bg-card-light dark:bg-card-dark p-4 shadow-sm border border-border-light dark:border-border-dark';
      itemEl.innerHTML = `
        <div class="flex items-center justify-center h-20 w-20 self-center rounded-full bg-primary/10">
          <span class="material-symbols-outlined !text-5xl text-primary">${icon}</span>
        </div>
        <div class="text-center">
          <p class="font-medium">${item.name}</p>
          <p class="text-sm text-text-secondary-light dark:text-text-secondary-dark">${item.description}</p>
        </div>
      `;
      
      this.outfitItems.appendChild(itemEl);
    });
  }

  toggleFavorite() {
    const index = this.favorites.indexOf(this.currentCity);
    const icon = this.favoriteBtn.querySelector('.material-symbols-outlined');
    
    if (index > -1) {
      this.favorites.splice(index, 1);
      icon.textContent = 'favorite_border';
      this.addChatMessage('assistant', `Removed ${this.currentCity} from favorites.`);
    } else {
      this.favorites.push(this.currentCity);
      icon.textContent = 'favorite';
      this.addChatMessage('assistant', `Added ${this.currentCity} to favorites!`);
    }
    
    this.savePreferences();
  }

  updateFavoriteButton() {
    const icon = this.favoriteBtn.querySelector('.material-symbols-outlined');
    if (this.favorites.includes(this.currentCity)) {
      icon.textContent = 'favorite';
    } else {
      icon.textContent = 'favorite_border';
    }
  }

  editPreferences() {
    // Show a modal-style edit interface in chat
    this.addChatMessage('assistant', `Let's update your preferences! I'll ask about each one:\n\n1. Style (e.g., Casual, Formal, Minimalist, Sporty)\n2. Clothing Types (e.g., Jackets, Jeans, Sneakers)\n3. Color Palette (e.g., Neutral, Blues, Earth Tones, Bold)`);
    
    const newStyle = prompt('Style preferences (comma-separated):', this.preferences.style.join(', '));
    if (newStyle) {
      this.preferences.style = newStyle.split(',').map(s => s.trim()).filter(s => s);
    }
    
    const newTypes = prompt('Clothing types (comma-separated):', this.preferences.clothingTypes.join(', '));
    if (newTypes) {
      this.preferences.clothingTypes = newTypes.split(',').map(s => s.trim()).filter(s => s);
    }
    
    const newColors = prompt('Color palette (comma-separated):', this.preferences.colorPalette.join(', '));
    if (newColors) {
      this.preferences.colorPalette = newColors.split(',').map(s => s.trim()).filter(s => s);
    }
    
    this.savePreferences();
    this.updatePreferencesDisplay();
    this.loadOutfitSuggestions();
    this.addChatMessage('assistant', `Perfect! I've updated your preferences:\n\n• Style: ${this.preferences.style.join(', ')}\n• Types: ${this.preferences.clothingTypes.join(', ')}\n• Colors: ${this.preferences.colorPalette.join(', ')}\n\nYour outfit suggestions have been refreshed!`);
  }

  submitFeedback(type) {
    console.log(`Feedback submitted: ${type} for ${this.currentCity}`);
    
    const message = type === 'positive' 
      ? 'Glad you like it! Let me know if you need anything else.'
      : 'Thanks for the feedback! Would you like me to suggest something different?';
    
    this.addChatMessage('assistant', message);
    
    // Visual feedback
    const btn = type === 'positive' ? this.thumbsUpBtn : this.thumbsDownBtn;
    btn.classList.add('bg-primary/20');
    setTimeout(() => btn.classList.remove('bg-primary/20'), 1000);
  }

  async sendMessage() {
    const message = this.chatInput.value.trim();
    if (!message) return;
    
    this.addChatMessage('user', message);
    this.chatInput.value = '';
    
    try {
      const payload = {
        message: message,
        city: this.currentCity,
        temperature: this.currentWeather?.temperature || 65,
        condition: this.currentWeather?.condition || 'partly cloudy',
        preferences: {
          style: this.preferences.style,
          types: this.preferences.clothingTypes,
          colors: this.preferences.colorPalette
        }
      };
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      this.addChatMessage('assistant', data.response);
      
      // If new outfit items were suggested, update the display
      if (data.items) {
        this.renderOutfitItems(data.items);
      }
    } catch (error) {
      console.error('Chat error:', error);
      this.addChatMessage('assistant', 'Sorry, I had trouble processing that. Could you try again?');
    }
  }

  addChatMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start gap-3' + (role === 'user' ? ' justify-end' : '');
    
    if (role === 'assistant') {
      messageDiv.innerHTML = `
        <div class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary">
          <span class="material-symbols-outlined">smart_toy</span>
        </div>
        <div class="flex-1 rounded-lg rounded-tl-none bg-background-light dark:bg-background-dark p-4 text-sm">
          <p>${this.escapeHtml(content)}</p>
        </div>
      `;
    } else {
      messageDiv.innerHTML = `
        <div class="flex-1 rounded-lg rounded-tr-none bg-primary p-4 text-sm text-white">
          <p>${this.escapeHtml(content)}</p>
        </div>
        <div class="flex size-8 shrink-0 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-700">
          <span class="material-symbols-outlined text-text-secondary-light dark:text-text-secondary-dark">person</span>
        </div>
      `;
    }
    
    this.chatMessages.appendChild(messageDiv);
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  showNotifications() {
    // Create a full-page overlay for notifications
    this.showOverlay('notifications');
  }

  showSettings() {
    // Create a full-page overlay for settings
    this.showOverlay('settings');
  }
  
  showOverlay(type) {
    // Remove existing overlay if any
    const existingOverlay = document.querySelector('.overlay');
    if (existingOverlay) {
      existingOverlay.remove();
    }
    
    const overlay = document.createElement('div');
    overlay.className = 'overlay fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
    
    const temp = this.currentWeather?.temperature || '--';
    const condition = this.currentWeather?.condition || 'unknown';
    
    if (type === 'notifications') {
      let weatherAlert = '';
      let alertClass = '';
      if (temp < 40) {
        weatherAlert = '❄️ ALERT: Very cold weather - dress warmly with layers!';
        alertClass = 'bg-blue-100 border-blue-500 text-blue-900';
      } else if (temp > 85) {
        weatherAlert = '☀️ ALERT: Very hot - stay hydrated and wear light clothing!';
        alertClass = 'bg-orange-100 border-orange-500 text-orange-900';
      } else if (condition.toLowerCase().includes('rain')) {
        weatherAlert = '🌧️ ALERT: Rain expected - bring waterproof gear!';
        alertClass = 'bg-sky-100 border-sky-500 text-sky-900';
      } else if (condition.toLowerCase().includes('snow')) {
        weatherAlert = '❄️ ALERT: Snow conditions - wear warm waterproof clothing!';
        alertClass = 'bg-cyan-100 border-cyan-500 text-cyan-900';
      }
      
      overlay.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-auto">
          <div class="p-6 border-b border-gray-200 flex justify-between items-center">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span class="material-symbols-outlined">notifications</span>
              Notifications
            </h2>
            <button class="close-overlay text-gray-500 hover:text-gray-700">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div class="p-6 space-y-4">
            ${weatherAlert ? `
            <div class="p-4 border-l-4 ${alertClass} rounded">
              <p class="font-semibold">${weatherAlert}</p>
            </div>
            ` : ''}
            <div class="space-y-2">
              <div class="flex items-center gap-2 text-gray-700">
                <span class="material-symbols-outlined text-primary">location_on</span>
                <span><strong>Current location:</strong> ${this.currentCity}</span>
              </div>
              <div class="flex items-center gap-2 text-gray-700">
                <span class="material-symbols-outlined text-primary">thermostat</span>
                <span><strong>Temperature:</strong> ${temp}°F (${condition})</span>
              </div>
              <div class="flex items-center gap-2 text-gray-700">
                <span class="material-symbols-outlined text-primary">favorite</span>
                <span><strong>Favorite cities:</strong> ${this.favorites.length > 0 ? this.favorites.join(', ') : 'None saved yet'}</span>
              </div>
              <div class="flex items-center gap-2 text-gray-700">
                <span class="material-symbols-outlined text-primary">check_circle</span>
                <span>Preferences saved and synced</span>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (type === 'settings') {
      overlay.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
          <div class="p-6 border-b border-gray-200 flex justify-between items-center">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span class="material-symbols-outlined">settings</span>
              Settings
            </h2>
            <button class="close-overlay text-gray-500 hover:text-gray-700">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div class="p-6 space-y-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span class="material-symbols-outlined">style</span>
                Outfit Preferences
              </h3>
              <div class="space-y-3 bg-gray-50 p-4 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-700">Style</p>
                  <p class="text-gray-900">${this.preferences.style.join(', ')}</p>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-700">Clothing Types</p>
                  <p class="text-gray-900">${this.preferences.clothingTypes.join(', ')}</p>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-700">Color Palette</p>
                  <p class="text-gray-900">${this.preferences.colorPalette.join(', ')}</p>
                </div>
                <button onclick="app.editPreferencesModal()" class="mt-3 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors">
                  Edit Preferences
                </button>
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span class="material-symbols-outlined">favorite</span>
                Favorite Cities
              </h3>
              <div class="bg-gray-50 p-4 rounded-lg">
                ${this.favorites.length > 0 ? 
                  `<ul class="space-y-2">${this.favorites.map(city => 
                    `<li class="flex items-center justify-between">
                      <span>${city}</span>
                      <button onclick="app.removeFavorite('${city}')" class="text-red-500 hover:text-red-700">
                        <span class="material-symbols-outlined text-sm">delete</span>
                      </button>
                    </li>`
                  ).join('')}</ul>` : 
                  '<p class="text-gray-600">No favorite cities yet. Click the heart icon to add one!</p>'
                }
              </div>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span class="material-symbols-outlined">info</span>
                Tips & Help
              </h3>
              <ul class="space-y-2 text-gray-700 bg-gray-50 p-4 rounded-lg">
                <li class="flex items-start gap-2">
                  <span class="material-symbols-outlined text-primary text-sm mt-0.5">check</span>
                  <span>Click "Edit" in preferences to customize your style</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="material-symbols-outlined text-primary text-sm mt-0.5">check</span>
                  <span>Use the heart icon to save favorite cities for quick access</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="material-symbols-outlined text-primary text-sm mt-0.5">check</span>
                  <span>Give thumbs up/down feedback to improve outfit suggestions</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="material-symbols-outlined text-primary text-sm mt-0.5">check</span>
                  <span>Ask me anything in the chat for personalized recommendations</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      `;
    }
    
    document.body.appendChild(overlay);
    
    // Close overlay handlers
    overlay.querySelector('.close-overlay').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.remove();
    });
  }
  
  editPreferencesModal() {
    // Close settings overlay first
    document.querySelector('.overlay')?.remove();
    
    // Use edit preferences function
    this.editPreferences();
  }
  
  removeFavorite(city) {
    this.favorites = this.favorites.filter(f => f !== city);
    localStorage.setItem('favorites', JSON.stringify(this.favorites));
    
    // Refresh settings overlay
    this.showSettings();
  }

  handleQuickAction(actionText) {
    // Handle quick action buttons with immediate responses
    this.addChatMessage('user', actionText);
    
    const temp = this.currentWeather?.temperature || 65;
    const city = this.currentCity.toLowerCase();
    const condition = (this.currentWeather?.condition || '').toLowerCase();
    
    // Hiking-related actions
    if (actionText.toLowerCase().includes('hiking')) {
      this.addChatMessage('assistant', `Great for hiking in ${this.currentCity} (${temp}°F)!\n\n• Moisture-wicking base layer\n• Lightweight hiking pants or athletic joggers\n• Waterproof hiking boots\n• Fleece or windbreaker jacket\n• Backpack with water and snacks\n${temp < 60 ? '\n• Extra layer (temperature might drop on the trail)' : ''}\n${condition.includes('rain') ? '\n• Rain jacket and waterproof pack cover essential!' : ''}\n\nStay safe and enjoy the trail!`);
    }
    // Camping-related actions
    else if (actionText.toLowerCase().includes('camping')) {
      this.addChatMessage('assistant', `For camping in ${this.currentCity} tonight (${temp}°F):\n\n• Warm layering system (base + fleece + jacket)\n• Insulated pants or thermal leggings\n• Warm socks and sturdy boots\n• Beanie and gloves\n• Waterproof outer layer\n• Don't forget: headlamp, sleeping bag rated for ${Math.round(temp - 10)}°F\n\nTemperature drops at night - dress warmer than daytime!`);
    }
    // Snow activities
    else if (actionText.toLowerCase().includes('snow') || actionText.toLowerCase().includes('skiing') || actionText.toLowerCase().includes('snowboarding')) {
      this.addChatMessage('assistant', `For snow activities in ${this.currentCity} (${temp}°F):\n\n• Waterproof snow jacket and pants\n• Thermal base layers (top and bottom)\n• Insulated gloves and warm socks\n• Winter hat and neck gaiter\n• Goggles and sunglasses\n• Hand warmers recommended!\n\nStay warm and have fun in the snow!`);
    }
    // Beach/pool activities
    else if (actionText.toLowerCase().includes('beach') || actionText.toLowerCase().includes('pool')) {
      this.addChatMessage('assistant', `Beach ready for ${this.currentCity} (${temp}°F)!\n\n• Swimsuit\n• Light cover-up or tank top\n• Flip flops or sandals\n• Sunglasses and sun hat\n• Sunscreen (SPF 30+)\n• Beach bag with towel\n\nStay hydrated and enjoy the sun!`);
    }
    // Outdoor activities (general)
    else if (actionText.toLowerCase().includes('outdoor')) {
      this.addChatMessage('assistant', `For outdoor activities in ${this.currentCity} (${temp}°F):\n\n• Breathable athletic wear\n• Comfortable sneakers\n• Light jacket (can tie around waist)\n• Sunglasses\n• Hat for sun protection\n${temp > 75 ? '\n• Stay hydrated - bring water!' : ''}\n\nPerfect weather to be outside!`);
    }
    // Rain gear check
    else if (actionText.toLowerCase().includes('rain')) {
      if (condition.includes('rain')) {
        this.addChatMessage('assistant', `Yes, rain gear needed in ${this.currentCity}!\n\n• Waterproof jacket with hood\n• Umbrella\n• Water-resistant pants or jeans\n• Waterproof boots\n\nRain is expected - stay dry!`);
      } else {
        this.addChatMessage('assistant', `No rain expected in ${this.currentCity} right now, but weather can change!\n\nBring a compact umbrella just in case. Better safe than soggy!`);
      }
    }
    // City walking
    else if (actionText.toLowerCase().includes('city') || actionText.toLowerCase().includes('walking')) {
      this.addChatMessage('assistant', `Perfect for city walking in ${this.currentCity} (${temp}°F)!\n\n• Comfortable jeans or casual pants\n• Layered top (t-shirt + light jacket)\n• Comfortable walking shoes\n• Crossbody bag or backpack\n${temp < 60 ? '\n• Light scarf for style and warmth' : ''}\n\nEnjoy exploring the city!`);
    }
    // Layering advice
    else if (actionText.toLowerCase().includes('layer')) {
      this.addChatMessage('assistant', `Layering tips for ${this.currentCity} (${temp}°F):\n\n1. Base: Moisture-wicking t-shirt\n2. Mid: Long-sleeve shirt or light sweater\n3. Outer: Jacket you can remove\n\nThis way you can adjust as temperature changes throughout the day!`);
    }
    // Formal options
    else if (actionText.includes('formal')) {
      if (temp < 60) {
        this.addChatMessage('assistant', `For formal occasions in ${this.currentCity} (${temp}°F), I recommend:\n\n• Dress shirt with a blazer\n• Dress pants\n• Leather dress shoes\n• A light overcoat would complete the look nicely\n\nWould you like me to adjust for a specific time of day?`);
      } else {
        this.addChatMessage('assistant', `For a formal setting in ${this.currentCity} (${temp}°F):\n\n• Dress shirt (you can skip the jacket since it's warm)\n• Dress pants\n• Leather shoes\n• Optional: lightweight blazer for indoors\n\nLet me know if you need accessories suggestions!`);
      }
    }
    // Colder weather prep
    else if (actionText.includes('colder')) {
      this.addChatMessage('assistant', `If it gets colder in ${this.currentCity}:\n\n• Add a warm sweater or fleece layer\n• Consider a thermal undershirt\n• Bring a scarf and gloves if temp drops below 45°F\n• Swap to warmer boots if available\n\nI'll keep monitoring the forecast for you!`);
    }
    // Mountain/altitude activities
    else if (actionText.toLowerCase().includes('mountain')) {
      this.addChatMessage('assistant', `For mountain activities in ${this.currentCity} (${temp}°F):\n\n• Layered clothing system\n• Hiking boots with good traction\n• Windproof jacket\n• Sun protection (altitude = stronger UV)\n• Extra layers (gets colder at elevation)\n\nTemperature drops about 3°F per 1000ft elevation!`);
    }
    else {
      // Generic response - send to backend
      this.chatInput.value = actionText;
      this.sendMessage();
    }
  }
  
  generateLocationQuickActions() {
    // Generate quick action buttons based on location and weather
    const city = this.currentCity.toLowerCase();
    const temp = this.currentWeather?.temperature || 65;
    const condition = (this.currentWeather?.condition || '').toLowerCase();
    const quickActionsContainer = document.querySelector('.quick-actions');
    
    console.log('Generating quick actions for:', city, temp, condition);
    
    if (!quickActionsContainer) {
      console.warn('Quick actions container not found!');
      return;
    }
    
    let actions = [];
    
    // Default actions
    actions.push('Any formal options?');
    actions.push('What if it gets colder?');
    
    // Location-specific actions - check more variations and be more inclusive
    // Pacific Northwest - rain/hiking/camping
    if (city.includes('seattle') || city.includes('tacoma') || city.includes('redmond') || 
        city.includes('bellevue') || city.includes('portland') || city.includes('vancouver') ||
        city.match(/\bwa\b/) || city.includes('washington') || city.includes('oregon')) {
      actions = ['Good for hiking?', 'Camping tonight?', 'Rain gear needed?'];
      console.log('Using Seattle/PNW actions for:', city);
    }
    // Snow/Mountain regions
    else if (city.includes('denver') || city.includes('aspen') || city.includes('boulder') ||
             city.includes('colorado') || city.includes('utah') || city.includes('tahoe') ||
             temp < 35 || condition.includes('snow')) {
      if (condition.includes('snow') || temp < 35) {
        actions = ['Snow activities?', 'Skiing outfit?', 'What about snowboarding?'];
        console.log('Using snow actions for:', city);
      } else {
        actions = ['Mountain hiking?', 'Cold weather gear?', 'What if it snows?'];
        console.log('Using mountain actions for:', city);
      }
    }
    // Beach/warm climates
    else if (city.includes('miami') || city.includes('los angeles') || city.includes('san diego') ||
             city.includes('austin') || city.includes('phoenix') || city.includes('tampa') ||
             city.match(/\bla\b/) || city.includes('california') || city.includes('florida') || temp > 75) {
      actions = ['Beach ready?', 'Pool party?', 'Outdoor activities?'];
      console.log('Using beach actions for:', city);
    }
    // Major cities
    else if (city.includes('new york') || city.includes('nyc') || city.includes('manhattan') ||
             city.includes('chicago') || city.includes('boston') || city.includes('philadelphia')) {
      actions = ['City walking?', 'Any formal options?', 'What about layering?'];
      console.log('Using city actions for:', city);
    }
    // Default
    else {
      console.log('Using default actions for:', city);
    }
    
    // Weather-specific adjustments
    if (condition.includes('rain')) {
      actions[2] = 'Will rain continue?';
    } else if (condition.includes('snow')) {
      actions[0] = 'Snow activities?';
    }
    
    // Update quick action buttons
    quickActionsContainer.innerHTML = actions.map(action => 
      `<button class="quick-action-btn px-4 py-2 bg-primary/10 text-primary rounded-full text-sm hover:bg-primary/20 transition-colors">${action}</button>`
    ).join('');
    
    console.log('Quick actions updated:', actions);
    
    // Re-attach event listeners
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const text = e.target.textContent.trim();
        this.handleQuickAction(text);
      });
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new WeatherOutfitApp();
});
