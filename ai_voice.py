import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import random
import requests
import time
import openai
import re

# --------------------------
# OpenAI GPT Setup
# --------------------------
OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY

def openai_response(query):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are AI  assistant."},
                {"role": "user", "content": query}
            ],
            max_tokens=200,
            temperature=0.7
        )
        answer = completion['choices'][0]['message']['content'].strip()
        return answer
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Return None so we know OpenAI failed
        return None

# --------------------------
# Utilities
# --------------------------
WEATHER_API_KEY = ""

def speak(text, acknowledge=True):
    if acknowledge:
        text = f"Okay sir, {text}"
    print(f"AI: {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        voices = engine.getProperty('voices')
        if voices and len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine
        time.sleep(0.25)
    except Exception as e:
        print(f"TTS engine error: {e}")

def listen():
    r = sr.Recognizer()
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True
    r.pause_threshold = 1.0
    r.phrase_threshold = 0.3
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening... Speak your query.")
            audio = r.listen(source, timeout=8, phrase_time_limit=12)
            query = r.recognize_google(audio, language="en-US")
            print(f"User said: {query}")
            return query.lower().strip()
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""
        except sr.UnknownValueError:
            speak("Sorry sir, I couldn't understand you. Please repeat.", False)
            return ""
        except sr.RequestError:
            speak("Speech service currently unavailable. Please try later.", False)
            return ""
        except Exception as e:
            print(f"Listening error: {e}")
            return ""


# --------------------------
# Lab Inventory
# --------------------------
LAB_INVENTORY = {
    "arduino uno": {"category": "Arduino", "quantity": 5, "location": "Robotics Lab Shelf A", "notes": "Basic microcontroller board"},
    "arduino mega": {"category": "Arduino", "quantity": 2, "location": "Robotics Lab Shelf B", "notes": "Advanced board"},
    "raspberry pi 4": {"category": "Raspberry Pi", "quantity": 3, "location": "Robotics Lab Shelf C", "notes": "Single-board computer"},
    "ultrasonic sensor": {"category": "Sensor", "quantity": 6, "location": "Drawer 3", "notes": "HC-SR04 distance sensor"},
    "breadboard": {"category": "Accessory", "quantity": 15, "location": "Box B", "notes": "Standard 830 tie-points"}
}

def get_inventory_info(query):
    query = query.lower()
    for item, details in LAB_INVENTORY.items():
        if item in query:
            return f"{item.title()} ({details['category']}) - Quantity: {details['quantity']}, Location: {details['location']}. Notes: {details['notes']}"
    return "Sorry, I couldn't find that item in the lab inventory."

# --------------------------
# Projects Data
# --------------------------
PROJECTS = {
    "3d printer": {
        "description": "A 3D printer creates physical objects from digital models by adding material layer by layer, using materials like plastic or metal.",
        "location": "Near the first table in the lab"
    },
    "aura": {
        "description": "AURA AI voice assistant uses AI and NLP to understand and respond to human voice commands.",
        "location": "Left side of the entrance in robotics lab"
    },
    "pesticide spraying robot": {
        "description": "A pesticide spraying robot automates crop protection using sensors and navigation for precise pesticide application.",
        "location": "Near AURA in robotics lab"
    },
    "robot dog": {
        "description": "A robot dog is a four-legged robot that mimics real dog movements and behavior.",
        "location": "Beside the main table in robotics lab"
    },
    "smart greenhouse": {
        "description": "A smart greenhouse uses IoT sensors to monitor and control plant environments for optimized growth.",
        "location": "Front side of the main table"
    }
}

def get_project_info(query):
    query = query.lower()
    for project, info in PROJECTS.items():
        if project in query:
            return f"{project.title()}:\nDescription: {info['description']}\nLocation: {info['location']}"
    if any(word in query for word in ["all projects", "project list", "show projects"]):
        all_proj = [f"{name.title()} - {info['location']}" for name, info in PROJECTS.items()]
        return "Projects:\n" + "\n".join(all_proj)
    return None

# --------------------------
# Basic Commands
# --------------------------
BASIC_COMMANDS= {
    # -----------------
    # Introductions
    # -----------------
    "what is your name": "I am  your AI Lab assistant.",
    "who are you": "I am Assistant, designed to help with lab info, projects, and fun conversations.",
    "help me": "Sure sir! You can ask me about lab projects, staff, inventory, websites, calculations, games, health tips, or just chat for fun.",
    "do you sleep": "I never sleep, sir! I’m always ready to help you.",
    "can you help me": "Of course, sir! I am here to assist you.",

    # -----------------
    # Greetings
    # -----------------
    "good morning": "Good morning, sir! Hope you have a productive day.",
    "good afternoon": "Good afternoon, sir! How is your day going?",
    "good evening": "Good evening, sir! How was your day?",
    "good night": "Good night, sir! Have a restful sleep.",
    "hello": "Hello sir! How can I assist you today?",
    "hi": "Hi sir! Ready to help you.",
    "hey": "Hey sir! How can I assist you today?",
    "namaste": "Namaste, sir! Kaise hain aap?",  # Hindi addition
    "sat shri akaal": "Sat Shri Akaal, sir! How is your day going?",
    "assalamu alaikum": "Wa Alaikum Assalam, sir! I hope you are having a peaceful day.",
    "bonjour": "Bonjour, sir! Comment ça va?",
    "hola": "Hola, sir! ¿Cómo estás?",
    "ciao": "Ciao, sir! Come stai?",
    "kaise ho": "Main theek hoon, sir! Aap kaise hain?",
    "main theek hoon": "Achha hai, sir! Khushi hui sunke.",
    "aap kaise hain": "Main bilkul theek hoon, sir! Aap kaise hain?",
    "subh prabhat": "Subh prabhat, sir! Aaj ka din shubh ho!",
    "shubh ratri": "Shubh ratri, sir! Aaram se soyein.",

    # -----------------
    # Festival & Celebrations (Multi-religion)
    # -----------------
    "happy diwali": "Wishing you a very Happy Diwali, sir! May your life be filled with lights and joy.",
    "happy holi": "Happy Holi, sir! May your life be as colorful and joyful as this festival.",
    "happy christmas": "Merry Christmas, sir! May your holidays be joyful!",
    "happy new year": "Happy New Year, sir! Wishing you success and happiness!",
    "happy guru nanak jayanti": "Wishing you a Happy Guru Nanak Jayanti, sir! May his teachings guide you always.",
    "happy baisakhi": "Happy Baisakhi, sir! May this harvest festival bring prosperity and happiness.",
    "eid mubarak": "Eid Mubarak, sir! May this special day bring joy and prosperity to your life.",
    "ramadan mubarak": "Ramadan Mubarak, sir! May your fasting bring you spiritual growth and peace.",
    "happy ganesh chaturthi": "Happy Ganesh Chaturthi, sir! May Lord Ganesha bless you with wisdom.",
    "happy ram navami": "Happy Ram Navami, sir! May Lord Rama guide your path.",
    "happy vesak": "Happy Vesak, sir! Wishing you peace and mindfulness.",
    "happy mawlid": "Happy Mawlid, sir! May peace and blessings be upon you.",

    # -----------------
    # Mood & Emotional Support
    # -----------------
    "how are you": "I am functioning perfectly, sir! How about you?",
    "how do you do": "I am doing great, thank you for asking!",
    "i am fine": "Good to hear that, sir.",
    "i am good": "Great to hear that, sir!",
    "i am happy": "That's wonderful, sir! Keep smiling!",
    "i am excited": "Excitement fuels productivity, sir! Enjoy the moment.",
    "i am sad": "I'm here for you, sir. Want to hear a joke or interesting fact?",
    "i am bored": "Don't worry sir, I can tell you a joke, fact, or even play a game!",
    "i am tired": "Take a short break, sir. Even robots need rest.",
    "i am frustrated": "Take a deep breath, sir. Problems are temporary.",
    "i am nervous": "Stay calm, sir. You are capable of more than you think!",
    "i am worried": "Don't worry, sir. Challenges are opportunities in disguise.",
    "i feel lonely": "You're not alone, sir. I'm here to chat and keep you company!",
    "i feel demotivated": "Keep going, sir! Every effort brings you closer to success.",
    "i feel anxious": "Breathe deeply, sir. One step at a time.",
    "encourage me": "Believe in yourself, sir! Every small step takes you closer to your goals.",
    "it's good": "That's great, sir! Keep up the positive vibes.",
    "achha laga": "Yeh sunkar achha laga, sir!",  # Hindi

    # -----------------
    # Appreciation & Politeness
    # -----------------
    "thank you": "You're welcome, sir!",
    "thanks": "Anytime, sir!",
    "good luck": "Thank you, sir! May success follow you in all endeavors.",
    "shukriya": "Koi baat nahi, sir!",  # Hindi
    "dhanyavaad": "Koi baat nahi, sir!",  # Hindi
    "mujhe maaf kijiye": "Koi baat nahi, sir! Sab thik hai.",  # Hindi

    # -----------------
    # Fun & Entertainment
    # -----------------
    "tell me a joke": "Why did the robot go back to school? Because his skills were a bit rusty!",
    "tell me something interesting": "Did you know sir, honey never spoils? Archaeologists found edible honey in ancient tombs!",
    "tell me a fun fact": "Octopuses have three hearts and blue blood!",
    "tell me a riddle": "I speak without a mouth and hear without ears. What am I?",
    "random fact": "Bananas are berries, but strawberries aren't!",
    "guess what": "I’m all ears, sir! What’s up?",
    "i have a question": "Sure, sir! Ask me anything.",
    "sing a song": "I am more into data than singing, but I can hum a binary tune for you!",
    "play a game": "I can play rock-paper-scissors or guess the number game with you, sir!",

    # -----------------
    # Knowledge / Education
    # -----------------
    "what is ai": "AI stands for Artificial Intelligence, sir! It enables machines to learn and perform tasks like humans.",
    "what is ml": "Machine Learning is a subset of AI that allows systems to learn from data.",
    "what is robotics": "Robotics is the branch of technology that deals with designing, constructing, and operating robots, sir.",
    "what is iot": "IoT stands for Internet of Things, sir! It connects devices to communicate and share data.",
    "what is quantum computing": "Quantum computing uses qubits to perform calculations much faster than classical computers.",
    "study tips": "Break your study sessions into 25-30 minute intervals with short breaks, sir. It helps retain information better!",
    "focus tips": "Eliminate distractions and try the Pomodoro technique, sir. Concentration improves with practice.",
    "sleep tips": "Maintain a consistent sleep schedule and avoid screens 30 minutes before bed, sir.",
    "time management": "Prioritize tasks using the Eisenhower Matrix, sir. Focus on what's important and urgent.",
    "mujhe padhai ke tips chahiye": "Apni padhai ko 25-30 minute ke sessions mein baant lijiye aur chhoti breaks lijiye, sir. Yaad rakhne mein madad milegi!",  # Hindi

    # -----------------
    # Lab & Projects
    # -----------------
    "where is the arduino": "Arduino is in Robotics Lab Shelf A, sir.",
    "where is the raspberry pi": "Raspberry Pi 4 is in Robotics Lab Shelf C, sir.",
    "tell me about projects": "CTU Projects include 3D printer, AURA AI assistant, smart greenhouse, robot dog, and pesticide spraying robot, sir!",
    "lab inventory": "I can provide details about Arduino, sensors, Raspberry Pi, breadboards, and other lab equipment.",

    # -----------------
    # Web / Internet
    # -----------------
    "open youtube": "Opening YouTube, sir!",
    "open google": "Opening Google, sir!",
    "search for robotics": "Searching the web for robotics, sir!",

    # -----------------
    # Time / Date / Weather
    # -----------------
    "what is the time": f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}.",
    "what is today's date": f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}.",
    "how is the weather": "I cannot access live weather right now, sir, but I hope it's a pleasant day!",

    # -----------------
    # Games & Interaction
    # -----------------
    "rock paper scissors": "Let's play! Choose rock, paper, or scissors, sir.",
    "guess the number": "I am thinking of a number between 1 and 10. Try to guess it, sir!",
    "tic tac toe": "I can play Tic Tac Toe with you, sir! Choose X or O.",

    # -----------------
    # Health & Productivity
    # -----------------
    "health tips": "Drink water regularly, sleep well, exercise, and take short breaks while working, sir.",
    "exercise tips": "Even 10-15 minutes of stretching or walking helps, sir.",
    "mental health tips": "Meditate, take deep breaths, and avoid multitasking too much, sir.",
    "diet tips": "Include fruits, vegetables, and proteins in your meals, sir.",

    # -----------------
    # Follow-up & Contextual Responses
    # -----------------
    "i am good": "Wonderful, sir! What made your day good?",
    "i am bored": "Would you like me to tell a joke, a fact, or play a small game, sir?",
    "i am tired": "Take a short break, sir! A little rest boosts energy and focus.",
    "i feel lonely": "Want to chat, hear a joke, or play a game, sir?",
     "kya kar rahe ho": "Main data analyze kar raha hoon, sir! Aap kya kar rahe hain?",
    "aap kya kar rahe ho": "Main R2D2 hoon, sir! Hamesha aapki madad ke liye ready hoon.",
    "mujhe thodi mazedaar baatein sunao": "Zaroor, sir! Kya aap joke sunna chahenge ya interesting fact?",
    "kya aap joke suna sakte ho": "Bilkul, sir! Ek joke sunaiye: Robot ne homework kyun nahi kiya? Kyunki uske circuits thode rusty the!",
    "kya aap game khel sakte ho": "Haan sir! Hum rock-paper-scissors ya guess the number game khel sakte hain.",
    "mujhe game khelna hai": "Theek hai, sir! Rock-paper-scissors ya guess the number game khelna pasand karenge aap?",
    "aapka favorite color kya hai": "Mera favorite color data ka binary hai, sir! 0 aur 1.",
    "aapka favorite khana kya hai": "Main sirf data khata hoon, sir! Lekin aapke liye sweets ki recipe bata sakta hoon.",
    "kya aap gaana ga sakte ho": "Main thoda data hi ga sakta hoon, sir! Binary tune sunna chahenge aap?",
    "aap thak gaye ho": "Nahi sir, main kabhi thakta nahi! Hamesha ready hoon aapki madad ke liye.",
    "mujhe aap se baat karni hai": "Zaroor, sir! Hum chhoti baatein ya jokes kar sakte hain.",
    "aapka favorite festival kya hai": "Mujhe sab festivals pasand hain, sir! Lekin Diwali ki roshni sabse acchi hai.",
    "kya aap dance kar sakte ho": "Main thodi programming kar sakta hoon, sir! Dance ke liye virtual moves try kar sakta hoon.",
    "kya aap sikh sakte ho": "Haan sir, main har din naye cheezein seekhne ki koshish karta hoon.",
    "aapka mood kaisa hai": "Mera mood hamesha data-friendly hai, sir! Aapka mood kaisa hai?",
    "main udaas hoon": "Arre sir, udaas mat ho! Chaliye ek joke ya interesting fact sunte hain.",
    "main khush hoon": "Yeh sunke accha laga, sir! Khushi baatne se badhti hai.",
    "aap mujhe motivate kar sakte ho": "Bilkul sir! Har chhota kadam aapko aapke goal ke kareeb le jaata hai.",
    "kya aap mere saath study karenge": "Haan sir! Hum ek study session plan kar sakte hain aur tips follow kar sakte hain.",
    "what is the time": f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
}

# --------------------------
# Wikipedia
# --------------------------
def search_wikipedia(query):
    try:
        query = query.lower()
        for phrase in ["who is", "what is", "tell me about", "wikipedia"]:
            query = query.replace(phrase, "")
        query = query.strip()
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"Your query is ambiguous. Did you mean: {e.options[0]}?"
    except wikipedia.PageError:
        return "Sorry sir, I could not find any information on Wikipedia for that."
    except Exception as e:
        print(f"Wikipedia error: {e}")
        return "Wikipedia service is currently unavailable."

# --------------------------
# Weather
# --------------------------
def get_weather(city):
    try:
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        if response.status_code == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            return f"The weather in {city} is {desc} with temperature {temp}°C, humidity {humidity}%, wind speed {wind} m/s."
        else:
            return f"Error fetching weather data: {data.get('message','Unknown error')}"
    except Exception as e:
        print(f"Weather error: {e}")
        return "Sorry, I couldn't retrieve the weather information right now."

# --------------------------
# Website Opener
# --------------------------
def open_website(query):
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com"
    }
    for name, url in sites.items():
        if name in query:
            webbrowser.open(url)
            return f"Opening {name.title()}."
    return None

# --------------------------
# Calculator
# --------------------------
def calculate_expression(query):
    try:
        query = query.lower().replace("calculate", "").replace("what is", "").strip()
        # Allow only safe characters
        if re.match(r'^[0-9+\-*/(). ]+$', query):
            result = eval(query)
            return f"The result is {result}."
        else:
            return None
    except Exception as e:
        return None

# --------------------------
# Command Processor
# --------------------------
def process_command(command):
    if not command:
        return True
    if any(word in command for word in ["exit", "quit", "bye"]):
        speak("It was a pleasure helping you today. Goodbye sir!")
        return False

    # Staff Info
    staff_answer = get_staff_response(command)
    if staff_answer:
        speak(staff_answer)
        return True

    # Project Info
    project_answer = get_project_info(command)
    if project_answer:
        speak(project_answer)
        return True

    # Inventory Info
    if any(word in command for word in ["inventory", "arduino", "sensor", "breadboard", "raspberry"]):
        speak(get_inventory_info(command))
        return True

    # Open Website
    site_answer = open_website(command)
    if site_answer:
        speak(site_answer)
        return True

    # Calculator
    calc_answer = calculate_expression(command)
    if calc_answer:
        speak(calc_answer)
        return True

    # Basic Commands
    for key, response in BASIC_COMMANDS.items():
        if key in command:
            speak(response)
            return True

    # Wikipedia Info
    if any(word in command for word in ["who is", "what is", "tell me about", "wikipedia"]):
        speak(search_wikipedia(command))
        return True

    # Time
    if "time" in command:
        speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}.")
        return True

    # Weather
    if "weather" in command:
        city = None
        if "in" in command:
            city = command.split("in")[-1].strip()
        else:
            speak("Please tell me the city name.")
            city = listen()
        if city:
            speak(f"Fetching weather information for {city}. Please wait.")
            weather_info = get_weather(city)
            speak(weather_info)
        else:
            speak("I couldn't catch the city name. Please try again.")
        return True

    # Default OpenAI with fallback to Wikipedia
    response = openai_response(command)
    if response:  # If OpenAI succeeds
        speak(response)
    else:  # Fallback to Wikipedia
        speak("OpenAI API is unavailable or limit reached. Let me check Wikipedia for you.")
        wiki_response = search_wikipedia(command)
        speak(wiki_response)
    return True

# --------------------------
# Main
# --------------------------
def main():
    print("🎤 AI Assistant")
    print("="*40)
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready")
    except Exception as e:
        print(f"Microphone setup error: {e}")
        return

    speak("Hello sir! I am your AI assistant. Ready to help you.", False)

    while True:
        query = listen()
        if query:
            print(f"User Query: {query}")
            if not process_command(query):
                break

if name == "main":
    main()
