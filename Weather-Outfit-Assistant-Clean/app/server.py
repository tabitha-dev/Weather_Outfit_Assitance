"""
Web Server for Weather Outfit Assistant

Simple Flask app that serves the UI and proxies requests to the ADK Coach agent.
"""

import os
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS


from weather_outfit_adk.monitoring import setup_logging, agent_metrics
from weather_outfit_adk.tools.weather_tools import get_current_weather, get_weather_smart
from .outfit_generator import generate_comprehensive_outfit

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# Setup logging
logger = setup_logging("web", enable_cloud_logging=False)

import random


def generate_chat_response(message, temperature, city, preferences=None):
    """Generate a friendly, conversational response based on message, weather, and preferences"""
    message_lower = message.lower()
    
    # Get style preference for personalization
    style = 'casual'
    if preferences and preferences.get('style'):
        style = preferences['style'][0].lower() if isinstance(preferences['style'], list) else preferences['style'].lower()
    
    # WEATHER ALERTS - Check for extreme conditions first
    if temperature >= 95:
        return f"⚠️ HEAT ALERT! It's {temperature}°F in {city} – that's dangerously hot! Wear light, breathable clothes, stay hydrated, use SPF 50+ sunscreen, seek shade, and limit outdoor activity during peak hours (10am-4pm). Heat exhaustion is real!"
    elif temperature >= 85:
        alert = f"🌡️ Hot day alert! {temperature}°F in {city}. "
        if 'what' in message_lower or 'wear' in message_lower or 'outfit' in message_lower:
            return alert + f"Wear light colors, breathable fabrics, shorts, tank tops, sunglasses, and use sunscreen! Stay hydrated!"
        return alert + f"Stay cool! What are you planning to do?"
    elif temperature <= 20:
        return f"🥶 EXTREME COLD! It's {temperature}°F in {city} – stay safe! Layer up with thermal underwear, insulated coat, warm hat, scarf covering your face, insulated gloves, and warm boots. Limit time outdoors and watch for frostbite!"
    elif temperature <= 32:
        alert = f"❄️ Freezing alert! {temperature}°F in {city}. "
        if 'what' in message_lower or 'wear' in message_lower or 'outfit' in message_lower:
            return alert + f"Bundle up! Wear a heavy coat, warm layers, gloves, scarf, hat, and insulated boots. Stay warm out there!"
        return alert + f"It's freezing! Need outfit advice?"
    
    # QUICK RESPONSE SHORTCUTS
    if "i'm cold" in message_lower or "im cold" in message_lower or "feeling cold" in message_lower:
        return f"Cold, huh? At {temperature}°F, add a warm layer! Try a fleece or sweater, maybe a scarf, and if it's really cold, throw on a jacket. Warm socks help too!"
    
    if "too hot" in message_lower or "i'm hot" in message_lower or "im hot" in message_lower or "feeling hot" in message_lower:
        return f"Too hot at {temperature}°F? Lighten up! Switch to breathable fabrics, lose a layer, wear lighter colors, and maybe roll up those sleeves. Stay hydrated!"
    
    if "dressy casual" in message_lower or "smart casual" in message_lower:
        return f"Dressy casual for {temperature}°F? Go with dark jeans or chinos, a button-down or nice blouse, clean sneakers or loafers, and a blazer or cardigan. Polished but not formal!"
    
    if "business casual" in message_lower or "office casual" in message_lower:
        return f"Business casual at {temperature}°F? Wear dress pants or a skirt, button-down shirt or blouse, closed-toe shoes (no sneakers!), and a blazer or cardigan. Professional and comfortable!"
    
    if "comfy" in message_lower or "comfortable" in message_lower or "cozy" in message_lower:
        return f"Comfort mode! At {temperature}°F in {city}, go with soft joggers or leggings, a cozy hoodie or sweater, your favorite sneakers, and maybe fuzzy socks. Maximum coziness!"
    
    # Greetings - check if message is ONLY a greeting (not part of another word like "hiking")
    is_greeting = message_lower.strip() in ['hi', 'hello', 'hey', 'good morning', 'morning', 'good afternoon', 'afternoon', 'good evening', 'evening', 'sup', 'yo']
    if is_greeting or (len(message.split()) <= 2 and any(g in message_lower.split() for g in ['hi', 'hello', 'hey', 'morning', 'afternoon', 'evening'])):
        greetings = [
            f"Hey there! It's about {temperature}°F in {city} right now. Got any plans today?",
            f"Hello! Looking at {temperature}°F in {city} today. What are you thinking of wearing?",
            f"Hi! The weather's {temperature}°F in {city}. Need some outfit ideas?"
        ]
        return random.choice(greetings)
    
    # Handle small talk BEFORE activities (jokes, fun facts, etc.)
    # Jokes
    if 'joke' in message_lower or 'funny' in message_lower:
        jokes = [
            f"Why did the scarf go to therapy? It had too many issues to unravel! 😄 Anyway, at {temperature}°F in {city}, do you need outfit suggestions?",
            f"What do clouds wear under their clothes? Thunderwear! ⛈️ Speaking of which, it's {temperature}°F in {city}. What are you up to today?",
            f"Why did the belt go to jail? For holding up a pair of pants! 👖 But seriously, at {temperature}°F, need help picking an outfit?",
            f"What did one hat say to the other? You stay here, I'll go on ahead! 🎩 Now, it's {temperature}°F in {city}. What can I help you wear?",
            f"Why don't jeans ever get lost? Because they always follow the waist! 👖 Speaking of jeans, at {temperature}°F, should you wear some?",
            f"What's a tornado's favorite game? Twister! 🌪️ Good thing it's only {temperature}°F in {city} today. Need outfit ideas?"
        ]
        return random.choice(jokes)
    
    # Fun facts about weather
    if 'fun fact' in message_lower or 'did you know' in message_lower or 'tell me something' in message_lower:
        facts = [
            f"Fun fact: The coldest temperature ever recorded was -128.6°F in Antarctica! Makes {temperature}°F in {city} feel pretty nice, right? What are you wearing today?",
            f"Did you know? The hottest temperature was 134°F in Death Valley! At {temperature}°F in {city}, you're in a much better spot. Need outfit suggestions?",
            f"Here's something cool: Rain smells so good because of petrichor – oils released by plants! It's {temperature}°F in {city} today. Planning anything fun?",
            f"Fun fact: Snowflakes can take up to an hour to fall from the cloud to the ground! At {temperature}°F in {city}, we won't see any today. What should you wear?"
        ]
        return random.choice(facts)
    
    # TRAVEL & PACKING FEATURES - Check these FIRST before activities
    if 'packing' in message_lower or 'pack for' in message_lower or 'trip to' in message_lower:
        if 'miami' in message_lower or 'florida' in message_lower or 'beach' in message_lower:
            return f"Packing for a beach trip? Bring: 3-4 swimsuits, light cotton clothes, shorts, tank tops, sundresses, flip-flops, sandals, one nice dinner outfit, sunscreen SPF 50+, sunglasses, beach hat, and a light cover-up!"
        elif 'new york' in message_lower or 'chicago' in message_lower or 'boston' in message_lower:
            return f"Packing for a city trip? Bring: Comfortable walking shoes, versatile jeans, 3-4 tops you can mix-match, a jacket, one dressy outfit, crossbody bag, portable charger, and layers for changing weather!"
        elif 'ski' in message_lower or 'snow' in message_lower or 'mountain' in message_lower:
            return f"Packing for a ski trip? Bring: Ski jacket, waterproof pants, thermal base layers (2-3 sets), warm socks, gloves, beanie, goggles, après-ski casual clothes, and sunscreen (snow reflects UV!)!"
        elif 'europe' in message_lower or 'paris' in message_lower or 'london' in message_lower:
            return f"Packing for Europe? Bring: Comfortable walking shoes, versatile neutral pieces, a light jacket, scarf, crossbody bag, dressy-casual outfits, layers, and an umbrella. Pack light – you'll walk a lot!"
        else:
            return f"Packing for a trip? Based on {temperature}°F in {city}, bring: 2-3 outfit changes per day, layers for temperature shifts, comfortable walking shoes, one dressy option, and weather-appropriate outerwear. Check forecast before you go!"
    
    elif '5 day' in message_lower or 'week trip' in message_lower or 'weekend' in message_lower and 'pack' in message_lower:
        return f"5-day trip packing list: 3 pants/shorts, 5-6 tops, 2 shoes (walking + dressy), 1 jacket, 1 sweater, underwear/socks, toiletries, chargers, and a versatile outfit for any occasion. Roll clothes to save space!"
    
    # Activity-based responses with personality
    # Check specific activities BEFORE general ones (e.g., "dog walk" before "walk")
    
    # Specific walk-related activities first
    elif 'dog walk' in message_lower or 'walking the dog' in message_lower or 'walking my dog' in message_lower:
        return f"Dog walk! At {temperature}°F in {city}, wear comfy walking shoes, weather-appropriate layers, and bring poop bags, water for your pup, and maybe treats. Leash check!"
    
    elif 'bird watch' in message_lower or 'birding' in message_lower:
        return f"Bird watching! Wear neutral/earth-toned clothes (you don't want to scare them!), comfortable walking shoes, layers, bring binoculars, a field guide, and bug spray. Quiet and patient wins!"
    
    # Coffee date before general date
    elif 'coffee' in message_lower and ('date' in message_lower or 'meet' in message_lower):
        return f"Coffee date! Keep it casual and comfortable at {temperature}°F – jeans, a nice top or sweater, your favorite sneakers or boots, and a jacket if it's cool. Be yourself!"
    
    elif 'hiking' in message_lower or 'trail' in message_lower or 'camping' in message_lower:
        return f"Ooh, hiking sounds fun! With {city}'s weather at {temperature}°F, I'd go with moisture-wicking layers, trail boots, and definitely bring a water bottle. Maybe throw in a hat and some bug spray too. And snacks – always snacks on the trail!"
    
    elif 'beach' in message_lower or 'pool' in message_lower or 'swim' in message_lower:
        return f"Beach day – nice! For {city}, pack your swimwear, flip-flops, a light cover-up, and definitely SPF 50+ sunscreen. Don't forget sunglasses, a beach towel, and maybe a waterproof bag for your phone. Have fun!"
    
    # General walking (after specific walk activities)
    elif 'walking' in message_lower or 'walk' in message_lower or 'stroll' in message_lower:
        if temperature < 50:
            return f"Nice! A walk in {city} at {temperature}°F? I'd wear comfortable walking shoes, a warm jacket, long pants, and maybe bring a scarf. Perfect weather for a cozy stroll!"
        else:
            return f"Perfect day for a walk! At {temperature}°F in {city}, wear comfy sneakers, breathable layers, and maybe sunglasses. Enjoy the fresh air!"
    
    elif 'dancing' in message_lower or 'dance' in message_lower or 'club' in message_lower or 'party' in message_lower:
        return f"Party time! For dancing at {temperature}°F, wear something you can move in – breathable top, comfortable pants or a dress, and shoes you can dance in all night. Maybe bring a light jacket for the walk home!"
    
    elif 'running' in message_lower or 'jog' in message_lower or 'jogging' in message_lower or ' run' in message_lower or message_lower.startswith('run'):
        if temperature < 45:
            return f"Running in {temperature}°F? Layer up! Moisture-wicking base layer, running tights, light jacket, gloves, and a headband to keep your ears warm. You'll heat up quick, so don't overdress!"
        else:
            return f"Great running weather at {temperature}°F! Wear moisture-wicking shirt, running shorts or leggings, good running shoes, and maybe a visor. Stay hydrated!"
    
    elif 'biking' in message_lower or 'bike' in message_lower or 'cycling' in message_lower:
        return f"Biking in {city}? At {temperature}°F, wear padded cycling shorts, moisture-wicking jersey, bike gloves, helmet, and bring a water bottle. Maybe throw on sunglasses too!"
    
    elif 'shopping' in message_lower or 'mall' in message_lower:
        return f"Shopping day! At {temperature}°F, wear comfortable shoes (you'll be walking a lot!), easy layers you can adjust, and bring a bag for your finds. Comfy and practical!"
    
    elif 'date' in message_lower or 'dinner' in message_lower or 'restaurant' in message_lower:
        if temperature < 50:
            return f"Date night! At {temperature}°F, I'd suggest a nice sweater or blouse, dark jeans or slacks, comfortable but stylish shoes, and a warm coat. Look good, feel good!"
        else:
            return f"Date night at {temperature}°F? Go with a nice shirt or dress, comfortable shoes, and light layers. Keep it classy but comfortable!"
    
    elif 'something fun' in message_lower or ('fun' in message_lower and len(message_lower) < 20 and 'fun fact' not in message_lower and 'funny' not in message_lower):
        return f"Something fun, huh? At {temperature}°F in {city}, wear comfy clothes you can move around in – jeans, a casual top, sneakers, and bring a light jacket just in case. Ready for whatever!"
    
    elif 'formal' in message_lower or 'event' in message_lower or 'wedding' in message_lower:
        if temperature < 50:
            return f"Formal event in cooler weather ({temperature}°F)? I'd suggest a sharp wool suit, button shirt, maybe a knit sweater underneath for warmth, and a thick overcoat. Leather gloves and a scarf will keep you cozy while looking good!"
        elif temperature > 70:
            return f"Warm formal occasion at {temperature}°F? Go light! A linen or cotton suit in a lighter color, breathable shirt, and skip the heavy layers. You'll stay cool and look sharp."
        else:
            return f"Nice! For formal stuff at {temperature}°F, a lightweight suit, cotton shirt, and light blazer should do it. Comfortable but classy!"
    
    elif 'travel' in message_lower or 'flight' in message_lower or 'airport' in message_lower:
        return "Travel day! Comfort is key. I'd wear layers, stretch pants, slip-on shoes for easy security, and bring a neck pillow and eye mask. Oh, and an empty water bottle to fill after security!"
    
    elif 'sport' in message_lower or 'exercise' in message_lower or 'gym' in message_lower or 'workout' in message_lower:
        return f"Workout time! At {temperature}°F, wear something moisture-wicking – athletic shirt, flexible shorts or pants, good shoes for your activity, and bring water. You got this!"
    
    elif 'work' in message_lower or 'office' in message_lower:
        return f"Work in {city}? At {temperature}°F, I'd go with comfortable walking shoes, weather-appropriate layers, and bring an umbrella just in case. Maybe a phone charger too!"
    
    elif 'yoga' in message_lower or 'pilates' in message_lower or 'stretching' in message_lower:
        return f"Yoga time! Wear stretchy leggings or yoga pants, a fitted tank or tee, and bring a yoga mat and water bottle. Layers are great if the studio is cool!"
    
    elif 'ski' in message_lower or 'skiing' in message_lower or 'snowboard' in message_lower:
        return f"Hitting the slopes! You'll need insulated ski jacket, waterproof pants, thermal base layers, ski gloves, goggles, helmet, and warm socks. Don't forget sunscreen – the sun reflects off snow!"
    
    elif 'concert' in message_lower or 'show' in message_lower or 'music' in message_lower:
        return f"Concert! At {temperature}°F, wear comfy shoes (you'll be standing), layers you can tie around your waist, and maybe earplugs. Leave valuables at home and bring just your essentials!"
    
    elif 'movie' in message_lower or 'cinema' in message_lower or 'theater' in message_lower:
        return f"Movie night! Theaters can be cold, so bring a light sweater or hoodie. Wear comfy clothes – jeans, a tee, and your favorite sneakers. Popcorn time!"
    
    elif 'study' in message_lower or 'library' in message_lower or 'studying' in message_lower:
        return f"Study session! Libraries can be chilly, so wear layers – hoodie, comfy pants, and easy shoes. Bring a water bottle and maybe some snacks for those long study hours!"
    
    elif 'picnic' in message_lower or 'park' in message_lower and temperature > 60:
        return f"Picnic in {city} at {temperature}°F sounds lovely! Wear breathable clothes, comfy sandals or sneakers, sunglasses, and bring sunscreen. Don't forget a blanket and your favorite snacks!"
    
    elif 'fishing' in message_lower or 'fish' in message_lower:
        return f"Gone fishing! At {temperature}°F in {city}, wear quick-dry pants, a long-sleeve shirt for sun protection, a fishing vest, water-resistant shoes, and a wide-brim hat. Bring sunscreen and bug spray!"
    
    elif 'golf' in message_lower or 'golfing' in message_lower:
        return f"Golf day! At {temperature}°F, wear a polo or golf shirt, comfortable pants or shorts (check course dress code), golf shoes, a visor or cap, and bring sunscreen. Don't forget your glove!"
    
    elif 'swimming' in message_lower or 'lap' in message_lower and 'swim' in message_lower:
        return f"Swimming! Bring your swimsuit, goggles, swim cap if needed, flip-flops for the deck, and a towel. Quick-dry clothes for after are super handy!"
    
    elif 'volunteer' in message_lower or 'volunteering' in message_lower:
        return f"Volunteering! Wear comfortable, practical clothes you don't mind getting dirty – closed-toe shoes, jeans or work pants, layers, and bring a water bottle. Thanks for giving back!"
    
    elif 'photoshoot' in message_lower or 'photos' in message_lower or 'pictures' in message_lower:
        return f"Photo time! At {temperature}°F, wear something that fits the vibe you want – solid colors photograph well, bring layers for variety, and comfortable shoes if you'll be walking. Have fun!"
    
    elif 'kayak' in message_lower or 'canoe' in message_lower or 'paddling' in message_lower:
        return f"Kayaking! At {temperature}°F in {city}, wear quick-dry clothes, water shoes, a life jacket (always!), sunscreen, a hat with a strap, and bring a waterproof bag for your phone!"
    
    elif 'climb' in message_lower or 'bouldering' in message_lower:
        return f"Rock climbing! Wear flexible climbing pants, a moisture-wicking shirt, climbing shoes, chalk bag, and bring plenty of water. Don't forget your harness and helmet for safety!"
    
    elif 'horse' in message_lower or 'riding' in message_lower or 'equestrian' in message_lower:
        return f"Horseback riding! Wear long pants (jeans work great), boots with a small heel, a fitted shirt, and bring gloves. A helmet is essential for safety!"
    
    elif 'brunch' in message_lower or 'breakfast' in message_lower or 'lunch' in message_lower:
        return f"Brunch time! At {temperature}°F, wear something casual but cute – nice jeans or a dress, comfortable shoes, sunglasses if outdoor seating, and bring a light jacket just in case!"
    
    elif 'garden' in message_lower or 'planting' in message_lower or 'yard work' in message_lower:
        return f"Gardening! At {temperature}°F, wear clothes you don't mind getting dirty – old jeans, long sleeves for sun protection, gardening gloves, a wide-brim hat, knee pads, and closed-toe shoes. Sunscreen!"
    
    elif 'sail' in message_lower or 'sailing' in message_lower or 'yacht' in message_lower:
        return f"Sailing! At {temperature}°F, wear non-slip boat shoes, quick-dry clothes, layers (it's windier on water!), polarized sunglasses, sunscreen, and bring a waterproof jacket!"
    
    elif 'surf' in message_lower or 'surfing' in message_lower:
        return f"Surfing! Bring your wetsuit (check water temp!), board shorts or swimsuit, rash guard, surf wax, sunscreen (waterproof), and a towel. Catch some waves!"
    
    elif 'paddleboard' in message_lower or 'paddle board' in message_lower or 'sup' in message_lower:
        return f"Paddleboarding! Wear a swimsuit, quick-dry shorts, rash guard, water shoes, life jacket, and bring sunscreen and a waterproof phone case. Balance is key!"
    
    elif 'wine' in message_lower or 'winery' in message_lower or 'wine tasting' in message_lower:
        return f"Wine tasting! At {temperature}°F, dress smart-casual – nice jeans or a dress, comfortable walking shoes (you'll be strolling vineyards!), layers, and bring a designated driver!"
    
    elif 'brewery' in message_lower or 'beer' in message_lower and 'tour' in message_lower:
        return f"Brewery tour! Keep it casual at {temperature}°F – jeans, a comfy shirt, sneakers, and bring your ID. Pace yourself and have fun!"
    
    # SEASONAL OUTFIT TIPS
    elif 'spring' in message_lower and ('outfit' in message_lower or 'wear' in message_lower or 'style' in message_lower):
        return f"Spring style! At {temperature}°F in {city}, go with light layers – a denim jacket, floral prints, pastel colors, ankle boots or sneakers, and always bring a light scarf. Perfect for unpredictable spring weather!"
    
    elif 'summer' in message_lower and ('outfit' in message_lower or 'wear' in message_lower or 'essentials' in message_lower):
        return f"Summer essentials for {temperature}°F: Breathable cotton or linen, shorts, sundresses, sandals, wide-brim hat, sunglasses, SPF 50+ sunscreen, and light colors to reflect heat. Stay cool!"
    
    elif 'fall' in message_lower and ('outfit' in message_lower or 'wear' in message_lower or 'style' in message_lower):
        return f"Fall vibes! At {temperature}°F, layer with a cozy sweater, dark jeans, ankle boots, a scarf, earth tones (burgundy, mustard, olive), and a medium-weight jacket. Pumpkin spice not included! 🍂"
    
    elif 'winter' in message_lower and ('outfit' in message_lower or 'wear' in message_lower or 'layer' in message_lower):
        return f"Winter layering guide: Start with thermal base layer, add a warm sweater, insulated coat, warm pants, winter boots, gloves, scarf, beanie. At {temperature}°F in {city}, you'll stay warm and stylish!"
    
    # ENHANCED WEATHER DETAILS
    elif 'windy' in message_lower or 'wind' in message_lower:
        if temperature < 60:
            return f"Windy and {temperature}°F in {city}? Wear wind-resistant jacket, layer underneath, long pants, close-fitting hat or headband, and avoid loose scarves that'll blow around. Wind makes it feel colder!"
        else:
            return f"Windy day at {temperature}°F? Go with fitted clothes, secure your hair, bring a light windbreaker, and wear sunglasses to protect from blowing dust. Windy but warm!"
    
    elif 'humid' in message_lower or 'humidity' in message_lower or 'sticky' in message_lower:
        return f"Humid weather at {temperature}°F in {city}? Wear moisture-wicking fabrics, loose-fitting clothes, breathable cotton or linen, light colors, and avoid heavy layers. Stay cool and dry!"
    
    elif 'uv' in message_lower or 'sun protection' in message_lower or 'sunburn' in message_lower:
        return f"Sun protection for {temperature}°F: SPF 50+ sunscreen (reapply every 2 hours!), wide-brim hat, UV-blocking sunglasses, light long sleeves for extra coverage, and seek shade between 10am-4pm!"
    
    # Weather-specific questions
    elif 'cold' in message_lower or 'colder' in message_lower:
        return f"Right now it's {temperature}°F. If it drops below 45°F, you'll want a scarf and gloves. Below freezing? Definitely need that thick insulated jacket!"
    
    elif 'rain' in message_lower:
        return f"For rainy days in {city}, I always recommend a waterproof jacket with a hood, water-resistant shoes, and an umbrella. Quick-dry pants are a lifesaver too!"
    
    elif 'snow' in message_lower:
        return "Snow! Bundle up with an insulated coat, thermal layers, snow boots, waterproof gloves, and a warm hat. If it's windy, grab some goggles too!"
    
    elif 'jacket' in message_lower or 'layer' in message_lower:
        if temperature < 60:
            return f"At {temperature}°F? Yeah, a jacket's a good call. A wind-resistant one or warm fleece would work great!"
        else:
            return f"It's pretty warm at {temperature}°F, but if you like an extra layer, go for a light cardigan or windbreaker!"
    
    # Questions about what to wear
    elif any(q in message_lower for q in ['what should', 'what to wear', 'outfit', 'recommend', 'suggest']):
        if temperature < 50:
            return f"At {temperature}°F in {city}, I'd layer up! A nice jacket over long sleeves and comfortable pants. Perfect for your {style} vibe!"
        elif temperature < 70:
            return f"The weather's pretty nice – {temperature}°F in {city}. Light jacket, comfy shirt, jeans... classic and works great for {style} style!"
        else:
            return f"It's warm! {temperature}°F in {city} means light, breathable clothes. Think shorts, cotton shirt, maybe sunglasses. Great weather!"
    
    # Handle friendly small talk and simple questions
    
    # Simple math
    if any(op in message_lower for op in ['+', '-', '*', '/', '=', 'plus', 'minus', 'times', 'divided']):
        # Try to answer simple math
        if '2+2' in message_lower or '2 + 2' in message_lower:
            return f"2+2 is 4! Easy one. 😊 Now, it's {temperature}°F in {city} today. Planning anything fun?"
        elif '1+1' in message_lower or '1 + 1' in message_lower:
            return f"1+1 equals 2! But here's a better number: {temperature}°F in {city}. Need outfit ideas?"
        else:
            return f"Hmm, math isn't really my thing! I'm better with outfit calculations. 😅 Like, at {temperature}°F in {city}, what should you wear? Want suggestions?"
    
    # How are you / chatbot status
    if any(phrase in message_lower for phrase in ['how are you', 'how r u', 'hows it going', "how's it"]):
        return f"I'm doing great, thanks for asking! Ready to help you look good in any weather. Speaking of which, it's {temperature}°F in {city} today. What's on your agenda?"
    
    # Thank you
    if any(phrase in message_lower for phrase in ['thank you', 'thanks', 'thx', 'ty']):
        return f"You're so welcome! Happy to help anytime. If you need more outfit advice for {city}'s {temperature}°F weather, just ask! 😊"
    
    # Compliments to the bot
    if any(phrase in message_lower for phrase in ['good bot', 'great job', 'awesome', 'helpful', 'you rock', 'amazing']):
        return f"Aww, thanks! That made my day! 🌟 Let me know if you need more outfit ideas for {city}'s weather!"
    
    # What's your name / who are you
    if 'your name' in message_lower or 'who are you' in message_lower:
        return f"I'm your Weather Outfit Assistant! I help you dress for any weather, any activity. Right now it's {temperature}°F in {city}. What can I help you wear today?"
    
    # Tough/complex off-topic questions that we can't answer
    complex_off_topic = ['recipe', 'cook', 'bake',
                         'code', 'program', 'html', 'javascript', 'python',
                         'history', 'science', 'chemistry', 'physics', 'biology',
                         'politics', 'president', 'election', 'government',
                         'news', 'stock', 'invest', 'crypto',
                         'movie plot', 'book summary', 'translate',
                         'what is the capital', 'when did', 'how old is',
                         'explain quantum', 'sports score']
    
    complex_patterns = [
        message_lower.startswith('who ') and 'wear' not in message_lower and len(message_lower) > 10,
        message_lower.startswith('when ') and 'wear' not in message_lower and len(message_lower) > 10,
        message_lower.startswith('why ') and 'weather' not in message_lower and 'wear' not in message_lower and len(message_lower) > 10,
        message_lower.startswith('how to ') and 'wear' not in message_lower and 'dress' not in message_lower,
        'tell me about' in message_lower and 'weather' not in message_lower,
    ]
    
    if any(keyword in message_lower for keyword in complex_off_topic) or any(complex_patterns):
        return f"I'm all about weather and outfit advice! Right now it's {temperature}°F in {city}. Want to know what to wear for an activity, or need outfit suggestions?"
    
    # Casual conversation / fallback
    else:
        responses = [
            f"Interesting! At {temperature}°F in {city}, you've got decent weather. What kind of outfit are you thinking?",
            f"Got it! With {city} at {temperature}°F, there's a lot you could wear. Any specific activities planned?",
            f"Right now it's {temperature}°F in {city}. Want some outfit ideas, or are you good?"
        ]
        return random.choice(responses)


@app.route('/')
def index():
    """Serve the main chat interface"""
    response = make_response(render_template('index.html'))
    # Prevent browser caching to ensure icon updates are always visible
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/api/weather', methods=['GET'])
def weather():
    """Get current weather data for a city with caching"""
    try:
        city = request.args.get('city', 'Redmond')
        
        logger.info(f"Weather request for city: {city}")
        
        # Fetch weather through the canonical cache.
        weather_data = get_weather_smart(city)
        
        logger.info(f"Weather response - City: {city}, Temp: {weather_data.get('temperature')}°F")
        
        return jsonify(weather_data)
        
    except Exception as e:
        logger.error(f"Weather error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/outfit', methods=['GET'])
def outfit():
    """Get outfit suggestions based on weather and preferences (reuses weather data from client)"""
    try:
        city = request.args.get('city', 'San Francisco')
        
        # Check if weather data was passed to avoid redundant API call
        temp = request.args.get('temperature', type=float)
        condition = request.args.get('condition', '')
        
        # Get user preferences
        style = request.args.get('style', 'Casual').split(',')
        clothing_types = request.args.get('types', 'Jackets,Jeans,Sneakers').split(',')
        colors = request.args.get('colors', 'Neutral,Blues').split(',')
        
        logger.info(f"Outfit request for city: {city}, style: {style}")
        
        # Only fetch weather if not provided (fallback)
        if temp is None or not condition:
            logger.info("Weather data not provided, fetching from API")
            weather_data = get_current_weather(city)
            temp = weather_data.get('temperature', 65)
            condition = weather_data.get('condition', 'partly cloudy')
        else:
            logger.info(f"Reusing weather data: {temp}°F, {condition}")
        
        # Generate outfit based on temperature, condition, and preferences
        # Check if activity is specified in request
        activity = request.args.get('activity', None)
        items = generate_comprehensive_outfit(temp, condition, style, clothing_types, colors, activity)
        
        return jsonify({
            'city': city,
            'temperature': temp,
            'items': items
        })
        
    except Exception as e:
        logger.error(f"Outfit error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with preference awareness - Routes to Coach Agent if available"""
    try:
        data = request.get_json(silent=True) or {}
        message = data.get('message', '')
        city = data.get('city', 'Redmond')
        preferences = data.get('preferences', {})
        session_id = data.get('session_id', 'default')
        user_id = data.get('user_id', 'anonymous')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        logger.info(f"Chat request - Session: {session_id}, City: {city}, Message: {message[:50]}...")
        
        # Track metrics
        with agent_metrics.measure_time("chat_request", labels={"endpoint": "chat"}):
            try:
                # Try to use ADK Coach Agent first
                agent_response = call_coach_agent(
                    message=f"{message} (City: {city})",
                    user_id=user_id,
                    session_id=session_id
                )
                
                if agent_response:
                    # Successfully got response from Coach Agent
                    logger.info("✅ Using Coach Agent response (A2A protocol)")
                    response_text = agent_response.get('response', agent_response.get('message', ''))
                    
                    # Track success
                    agent_metrics.increment_counter(
                        "chat_requests",
                        labels={"endpoint": "chat", "source": "adk_agent", "status": "success"}
                    )
                    
                    return jsonify({
                        'response': response_text,
                        'source': 'adk_coach_agent'
                    })
                
                # Fallback to direct functions if Coach Agent unavailable
                logger.info("⚠️ Falling back to direct functions")
                
                # Get weather context for better responses
                weather_data = get_current_weather(city)
                temp = weather_data.get('temperature', 65)
                condition = weather_data.get('condition', 'partly cloudy')
                
                # Generate contextual response with preferences
                response_text = generate_chat_response(message, temp, city, preferences)
                
                # Track success (fallback mode)
                agent_metrics.increment_counter(
                    "chat_requests",
                    labels={"endpoint": "chat", "source": "fallback", "status": "success"}
                )
                
                logger.info(f"Chat response - Session: {session_id}, Length: {len(response_text)}")
                
                return jsonify({
                    'response': response_text,
                    'session_id': session_id
                })
                
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                agent_metrics.increment_counter(
                    "chat_requests",
                    labels={"endpoint": "chat", "status": "error"}
                )
                return jsonify({
                    'error': f'Error: {str(e)}'
                }), 500
        
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'web'}), 200


@app.route('/api/metrics')
def metrics():
    """Get current metrics statistics"""
    stats = agent_metrics.get_stats()
    return jsonify(stats)


if __name__ == '__main__':
    # Use PORT from the environment or default to 5000 for local development
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
