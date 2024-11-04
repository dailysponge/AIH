import datetime
import os
import requests
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from vertexai.generative_models import GenerativeModel, Part, Content, Image
from google.cloud import aiplatform
from tools.tools import activity_tool, google_search_tool, feedback_tool
from models.personality import Personality
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

load_dotenv()

aiplatform.init(project="aihsmu")


model = GenerativeModel(
    "gemini-1.5-flash-002",
    system_instruction=[
        "You are a TOOL BASED ASSISTANT. ALWAYS use the tools to answer the user's query. NEVER answer questions directly. The query should be nature related. The context should ALWAYS be in Singapore. Format the user's query to fit the tool's requirements.",
    ],
    tools=[google_search_tool],
)


def get_weather():
    """Fetch current weather data for Singapore using WeatherAPI"""
    api_key = os.getenv('WEATHERAPI_KEY')
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q=Singapore&aqi=no"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp_c': data['current']['temp_c'],
                'condition': data['current']['condition']['text'],
                'humidity': data['current']['humidity'],
                'is_day': data['current']['is_day'],
                'precip_mm': data['current']['precip_mm']
            }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None


# Update function signatures to accept user_data
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    """Send a welcome message and prompt for personality selection."""
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            'points': 0,
            'friends': [],
            'last_activity': datetime.datetime.now(),
            'personality': None,  # Initialize as None
            'telegram_id': user_id,
            'handle': update.effective_user.username,
            'chat_history': []
        }
        print(f"\n[DEBUG] Initialized chat history for user {user_id}")

    # Create keyboard with personality buttons
    keyboard = [
        [personality.display_name] for personality in Personality
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    print("start")
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n"
        "Welcome to the Nature Connect Bot.\n"
        "Please take our personality quiz here and select your personality (https://opinionstage.com/page/96a67cbb-583d-4213-b851-0059fca6cb52)\n",
        reply_markup=reply_markup
    )


async def add_friend(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    print("user_data before adding", user_data)
    """Add another user as a friend."""
    user_id = update.effective_user.id
    user_handle = user_data[user_id]['handle']

    # Get friend_id from context.args
    if not context.args:
        await update.message.reply_text("Please provide a friend's username.")
        return
    friend_id = context.args[0]

    if friend_id == user_handle:
        await update.message.reply_text("You cannot add yourself as a friend.")
        return

    # Find the friend's user ID from the handle
    friend_user_id = None
    for uid, data in user_data.items():
        if data['handle'] == friend_id:
            friend_user_id = uid
            break

    if friend_user_id is None:
        await update.message.reply_text(f"User @{friend_id} not found.")
        return

    # Avoid duplicate friends
    if friend_user_id not in user_data[user_id]['friends']:
        user_data[user_id]['friends'].append(friend_user_id)
        # award points to user for adding a friend
        user_data[user_id]['points'] += 10
        await update.message.reply_text(f"User @{friend_id} has been added to your friends list.\n You have earned 10 points for adding a friend.")
    # Update friend's friend list
    if user_id not in user_data[friend_user_id]['friends']:
        user_data[friend_user_id]['friends'].append(user_id)
    else:
        await update.message.reply_text(f"User @{friend_id} is already in your friends list.")
    print("user_data after adding", user_data)


async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    """Show the leaderboard of all users and their points."""
    # Sort users by points in descending order
    sorted_users = sorted(
        user_data.items(),
        key=lambda x: x[1]['points'],
        reverse=True
    )

    # Create leaderboard message with proper escaping
    leaderboard_lines = ["🏆 *Nature Connect Leaderboard* 🏆\n"]

    for i, (user_id, data) in enumerate(sorted_users, 1):
        # Escape special characters in handle/points
        handle = data.get('handle', 'Anonymous')
        if handle:
            # Escape special characters: . ! - ( )
            handle = handle.replace('.', '\\.').replace('!', '\\!').replace(
                '-', '\\-').replace('(', '\\(').replace(')', '\\)')
        points = str(data.get('points', 0))

        # Format the line with position emoji
        if i == 1:
            emoji = "🥇"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = "🌟"

        line = f"{emoji} {i}\\. @{handle}: {points} points\n"
        leaderboard_lines.append(line)

    if not leaderboard_lines[1:]:  # If no users except header
        leaderboard_lines.append(
            "No scores yet\\! Start completing activities to earn points\\! 🌿")

    leaderboard_message = "".join(leaderboard_lines)

    await update.message.reply_text(leaderboard_message, parse_mode='MarkdownV2')


async def notify_friends(update, context, user_data):
    """Send notifications to friends when a user completes an activity."""
    user_handle = update.effective_user.username
    user_id = update.effective_user.id
    user_friends = user_data[user_id]['friends']
    for friend_id in user_friends:
        if friend_id in user_data:
            # Send a notification to the friend
            try:
                await context.bot.send_message(chat_id=friend_id, text=f"🎉 Your friend User @{user_handle} has completed an activity! Are you ready to start your adventure?")
            except Exception as e:
                print(f"Error notifying User {friend_id}: {e}")


def google_search(query):
    """Perform a Google search and return the results."""
    search_api_url = "https://www.googleapis.com/customsearch/v1"
    print("user message", query)
    params = {
        'q': query,
        'key': os.getenv('GOOGLE_API_KEY'),
        'cx': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
    }
    response = requests.get(search_api_url, params=params)
    if response.status_code == 200:
        res = response.json()
        results = []
        for item in res.get('items', [])[:10]:
            results.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet'),
            })
        print('google search results', results)
        return results
    else:
        print(f"Error performing Google search: {response.status_code}")
        return None


async def handle_user_image(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    """Handle user images, and let VertexAI model process them."""
    try:
        user_id = update.effective_user.id
        model = GenerativeModel(
            "gemini-1.5-flash-002",
            system_instruction=[
                "Analyze the image and provide a brief description of the picture in the context of nature in Singapore. Craft your response in a fun and engaging manner with a moderate use of emojis and fun facts.",
            ],
        )
        print("user message has photo")
        # Get the largest photo (best quality)
        photo = update.message.photo[-1]
        image_file = await context.bot.get_file(photo.file_id)
        image_bytearray = await image_file.download_as_bytearray()
        image_bytes = bytes(image_bytearray)

        # Create an Image object from the bytes
        image = Image.from_bytes(image_bytes)

        # If there's a caption, use it as the user's message
        user_message = update.message.caption or "Describe this image in the context of nature in Singapore."

        # Create a content object with both text and image
        response = model.generate_content(
            [image, user_message]
        )
        print("img response", response.text)
        await update.message.reply_text(response.text)
        points_awarded = 5  # You can adjust this value as needed
        user_data[user_id]['points'] += points_awarded

        # Send a message about the points awarded
        await update.message.reply_text(f"🎉 You've earned {points_awarded} points for asking about this image! Your total is now {user_data[user_id]['points']} points.")
    except Exception as e:
        print(f"Error processing image: {e}")
        await update.message.reply_text("An error occurred while processing your image. Please try again later.")


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for MarkdownV2 formatting while preserving bold formatting"""
    # First, temporarily replace double asterisks with a placeholder
    text = text.replace('**', '§BOLD§')

    # Escape special characters
    special_chars = ['_', '*', '[', ']',
                     '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f"\\{char}")

    # Restore double asterisks for bold text
    text = text.replace('§BOLD§', '*')

    return text


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Check if the message is a personality selection
    if user_message in Personality.get_all_display_names():
        try:
            personality = Personality.from_display_name(user_message)
            user_data[user_id]['personality'] = personality.traits_string

            await update.message.reply_text(
                personality.welcome_message,
                reply_markup=ReplyKeyboardRemove()
            )
            return
        except ValueError:
            await update.message.reply_text(
                "Sorry, that's not a valid personality type. Please use the buttons to select your personality.",
                reply_markup=ReplyKeyboardMarkup(
                    [[p.display_name] for p in Personality],
                    one_time_keyboard=True
                )
            )
            return

    # If no personality is set, prompt user to select one
    if user_id not in user_data or not user_data[user_id].get('personality'):
        keyboard = [[p.display_name] for p in Personality]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "Please select your personality type first:",
            reply_markup=reply_markup
        )
        return

    # Continue with the existing message handling logic
    print("user message has text")
    weather_data = get_weather()

    model = GenerativeModel(
        "gemini-1.0-pro",
        system_instruction=[
            "You are a TOOL BASED nature-related ASSISTANT. Engage in brief, fun conversations with the user to understand their needs and emotions, and guide them to find nature-related activities. Always answer in first person.",
            "ALWAYS consider the user's personality when suggesting activities and adjust the suggestions accordingly.",
            "After suggesting activities, ALWAYS ask for feedback about the suggestions.",
            "If the user provides feedback or or has said that they completed an activity, you MUST ALWAYS use the handle_feedback tool to process it.",
            "Use tools to answer the user's query if needed, especially for nature-related activities. The context should ALWAYS be in Singapore.",
            "When suggesting activities, ALWAYS consider the current weather conditions provided:",
            f"Temperature: {weather_data['temp_c']}°C",
            f"Condition: {weather_data['condition']}",
            f"Precipitation: {weather_data['precip_mm']}mm",
            f"Time of day: {'Day' if weather_data['is_day'] else 'Night'}",
            "ALWAYS keep your responses short, concise and well-formatted under 100 words, and maintain a fun demeanor with the moderate use of emojis. 🎉😊",
            "Don't use double asterisks (**) for emphasis - use single asterisks (*) for highlighting important points.",
        ],
        tools=[google_search_tool, feedback_tool],
    )
    user_id = update.effective_user.id
    user_personality = user_data[user_id]['personality']
    user_message = update.message.text

    # Get chat history
    chat_history = user_data[user_id]['chat_history']

    # Create content parts with chat history
    content_parts = []

    # Add chat history (last 5 messages)
    for msg in chat_history[-5:]:
        content_parts.append(Part.from_text(
            f"{'Assistant' if msg['role'] == 'assistant' else 'User'}: {msg['content']}"))

    # Add current message
    content_parts.append(Part.from_text(
        f"My personality is {user_personality}. Current message: {user_message}"
    ))

    user_prompt_content = Content(
        role="user",
        parts=content_parts,
    )

    # Generate content using the model
    try:
        res = model.generate_content(
            user_prompt_content,
            tools=[google_search_tool],
        )
    except Exception as e:
        print(f"Error generating content: {e}")
        await update.message.reply_text("An error occurred while processing your request.")
        return

    print("res", res)

    # After getting chat history
    chat_history = user_data[user_id]['chat_history']
    print(f"\n[DEBUG] Current chat history for user {user_id}:")
    for msg in chat_history:
        print(f"Role: {msg['role']}, Time: {msg['timestamp']}")
        print(f"Content: {msg['content']}\n")

    # After adding user message
    chat_history.append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.datetime.now().isoformat()
    })
    print(f"\n[DEBUG] Added user message to chat history for user {user_id}")

    print(
        f"\n[DEBUG] Current chat history for user {user_id}: after adding user message")
    for msg in chat_history:
        print(f"Role: {msg['role']}, Time: {msg['timestamp']}")
        print(f"Content: {msg['content']}\n")

    response_text = None
    # Extract the response and function calls
    response_content = res.candidates[0].content
    function_calls = res.candidates[0].function_calls
    print("function_calls", function_calls)

    if function_calls:
        for function_call in function_calls:
            if function_call.name == "handle_feedback":
                function_args = function_call.args
                if function_args.get("is_feedback", False):
                    # Award points for feedback
                    user_data[user_id]['points'] += 10

                    response_text = "Thank you for your feedback! 🌟 You've earned 10 points for completing and activity and sharing your thoughts! 🎉"
                    await update.message.reply_text(response_text)
                    return

            elif function_call.name == "suggest_activities":
                function_args = function_call.args
                function_args["personality"] = user_personality
                try:
                    response = model.generate_content(
                        [
                            user_prompt_content,
                            response_content,
                            Content(
                                parts=[
                                    Part.from_function_response(
                                        name=function_call.name,
                                        response=function_args
                                    )
                                ]
                            )
                        ]
                    )
                    response_text = response.text + \
                        "\n\nHow do you feel about these suggestions? I'd love to hear your feedback! 🤗"
                    await update.message.reply_text(response_text)
                except Exception as e:
                    print(f"Error handling suggest_activities: {e}")
                    await update.message.reply_text("An error occurred while suggesting activities.")

            elif function_call.name == "question_answer_tool":
                function_args = function_call.args
                search_results = google_search(function_args["query"])
                print("search_results", search_results)
                if search_results:
                    try:
                        # Format the search results
                        response_text = "\n".join(
                            [f"{result['title']}: {result['snippet']} \n Link: {result['link']}" for result in search_results]
                        )
                        print("response_text", response_text)
                        # Pass the search results back to the model
                        response = model.generate_content(
                            [
                                user_prompt_content,
                                response_content,
                                Content(
                                    parts=[
                                        Part.from_function_response(
                                            name=function_call.name,
                                            response={
                                                "content": response_text,
                                            }
                                        )
                                    ]
                                )
                            ],
                        )
                        response_text = response.text
                        # await update.message.reply_text(response.text)
                    except Exception as e:
                        print(f"Error handling google_search: {e}")
                        await update.message.reply_text("An error occurred while processing the search results.")
                else:
                    await update.message.reply_text("No search results found.")
            else:
                await update.message.reply_text("No tool calls detected.")
    else:
        print("using LLM directly, not calling tool")
        response_text = response_content.text
        # Remove "Assistant: " prefix if it exists
        response_text = response_text.replace("Assistant: ", "")

        # Check for activity completion
        is_activity_completed = await check_activity_completion(user_message)
        print("is_activity_completed", is_activity_completed)
        if is_activity_completed:
            print("activity completed")
            # Award points for completing activity
            user_data[user_id]['points'] += 20
            # Notify friends
            await notify_friends(update, context, user_data)
            response_text += "\n\n🎉 Congratulations on completing the activity! You've earned 20 points! 🌟"

    # After adding assistant response
    if response_text:
        # Clean the response text before adding to chat history
        cleaned_response = response_text.replace("Assistant: ", "")
        chat_history.append({
            'role': 'assistant',
            'content': cleaned_response,
            'timestamp': datetime.datetime.now().isoformat()
        })
        print(
            f"\n[DEBUG] Added assistant response to chat history for user {user_id}")
        print(f"Chat history length: {len(chat_history)}")

        # Limit chat history to last 20 messages to prevent memory issues
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]

        user_data[user_id]['chat_history'] = chat_history

        # Escape special characters before sending
        escaped_response = escape_markdown_v2(cleaned_response)
        print(f"\n[DEBUG] Escaped response: {escaped_response}")  # Debug print

        try:
            await update.message.reply_text(escaped_response, parse_mode='MarkdownV2')
        except Exception as e:
            print(f"Error sending formatted message: {e}")
            # Fallback to plain text if formatting fails
            await update.message.reply_text(cleaned_response, parse_mode=None)


async def handle_personality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    """Handle the personality selection from the user."""
    user_id = update.effective_user.id
    selected_personality = update.message.text

    # Personality-specific welcome messages
    welcome_messages = {
        "Adventurous Andy": (
            "🏃‍♂️ Perfect choice for an adventure seeker!\n\n"
            "I'm here to help you discover exciting outdoor activities and nature spots in Singapore. "
            "Whether you're looking for hiking trails, water sports, or adrenaline-pumping adventures, "
            "I've got you covered!\n\n"
            "How can I help you start your next adventure today? 🌿🗺️"
        ),
        "Spontaneous Sammy": (
            "🎯 Ah, a free spirit! Love it!\n\n"
            "Ready to discover some spontaneous nature activities? "
            "I can suggest quick getaways and last-minute nature spots that match your flexible style.\n\n"
            "What kind of adventure are you up for today? 🌳✨"
        ),
        "Planet Pete": (
            "🌍 Welcome, fellow earth guardian!\n\n"
            "I'm here to help you connect with nature while protecting our environment. "
            "From eco-friendly activities to conservation efforts, "
            "let's make a positive impact together.\n\n"
            "What environmental interests would you like to explore today? 🌱"
        ),
        "Chill Charlie": (
            "😌 Perfect choice for a relaxed nature lover!\n\n"
            "I know all the peaceful spots and calming nature activities in Singapore. "
            "From quiet gardens to serene water spots, "
            "we'll find your perfect zen moment.\n\n"
            "How would you like to unwind in nature today? 🍃"
        ),
        "Gamer George": (
            "🎮 Level up your nature experience!\n\n"
            "I can help you find outdoor activities that match your strategic mindset. "
            "Think of it as a real-world adventure game with achievements to unlock!\n\n"
            "Ready to start your nature quest? What's your first mission? 🎯"
        ),
        "Trendy Tiara": (
            "📱 Welcome to your nature-meets-social journey!\n\n"
            "I'll help you discover Instagram-worthy nature spots and trending outdoor activities. "
            "Let's find the perfect blend of nature and social sharing.\n\n"
            "What kind of trendy nature experience are you looking for today? 🌺"
        )
    }

    try:
        personality = Personality.from_display_name(selected_personality)
        user_data[user_id]['personality'] = personality.traits_string

        # Send the personality-specific welcome message
        welcome_message = welcome_messages.get(selected_personality,
                                               "How can I help you today? Feel free to ask me about nature activities in Singapore! 🌿")

        await update.message.reply_text(
            welcome_message,
            reply_markup=ReplyKeyboardRemove()
        )
    except ValueError:
        await update.message.reply_text(
            "Sorry, that's not a valid personality type. Please use the buttons to select your personality.",
            reply_markup=ReplyKeyboardMarkup(
                [[p.display_name] for p in Personality],
                one_time_keyboard=True
            )
        )


async def check_activity_completion(user_message: str) -> bool:
    """Check if user's message indicates activity completion using LLM."""
    activity_check_model = GenerativeModel(
        "gemini-1.0-pro",
        system_instruction=[
            "You are an activity completion detector. Your ONLY job is to determine if the user's message indicates they have completed a nature-related activity.",
            "If the message indicates activity completion, respond ONLY with 'activity completed'.",
            "If not, respond ONLY with 'no activity'.",
            "Example completions:",
            "- 'I just finished hiking at MacRitchie!' → 'activity completed'",
            "- 'The weather is nice today' → 'no activity'",
            "- 'Had a great time at the Botanic Gardens!' → 'activity completed'",
            "- 'Can you suggest something to do?' → 'no activity'",
            "- 'I just listened to nature sounds online and it helped calm me down alot' → 'activity completed'"
        ]
    )

    try:
        print("THIS IS THE USER MESSAGE", user_message)
        response = activity_check_model.generate_content(user_message)
        return response.text.strip().lower() == "activity completed"
    except Exception as e:
        print(f"Error checking activity completion: {e}")
        return False
