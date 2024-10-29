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
from tools.tools import activity_tool, google_search_tool

load_dotenv()

aiplatform.init(project="aihsmu")


model = GenerativeModel(
    "gemini-1.5-flash-002",
    system_instruction=[
        "You are a TOOL BASED ASSISTANT. ALWAYS use the tools to answer the user's query. NEVER answer questions directly. The query should be nature related. The context should ALWAYS be in Singapore. Format the user's query to fit the tool's requirements.",
    ],
    tools=[google_search_tool],
)


# Update function signatures to accept user_data
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    """Send a welcome message and prompt for the personality quiz."""
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            'points': 0,
            'friends': [],
            'last_activity': datetime.datetime.now(),
            'personality': "Energetic, Adventurous, Outdoorsy, Lively, Dynamic, Bold, Active, Resilient, Fearless, Enthusiastic, Curious, Nature-loving",
            'telegram_id': user_id,
            'handle': update.effective_user.username,
            'chat_history': []
        }
        print(f"\n[DEBUG] Initialized chat history for user {user_id}")

    print("start")
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n"
        "Welcome to the Nature Connect Bot.\n"
        "Please take our personality quiz here: [Personality Quiz](https://your-quiz-link.com)\n",
        parse_mode='Markdown'
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
    """Show the leaderboard of users based on points. Return None if no friends are added."""
    if not user_data[update.effective_user.id]['friends']:
        await update.message.reply_text("You don't have any friends yet. Add some friends to see the leaderboard.")
        return
    leaderboard_users = sorted(
        user_data.items(), key=lambda x: x[1]['points'], reverse=True)
    leaderboard_message = "🏆 *Leaderboard* 🏆\n"
    for rank, (_, data) in enumerate(leaderboard_users, start=1):
        leaderboard_message += f"{rank}. @{data['handle']}: {data['points']} points\n"
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
                "Analyze the image and provide a brief description of the picture in the context of nature in Singapore. Craft your response in a fun and engaging manner with the use of emojis and fun facts.",
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
    print("user message has text")
    model = GenerativeModel(
        "gemini-1.0-pro",
        system_instruction=[
            "You are a TOOL BASED nature-related ASSISTANT. Engage in brief, fun conversations with the user to understand their needs and emotions, and guide them to find nature-related activities. Use tools to answer the user's query if needed, especially for nature-related activities. The context should ALWAYS be in Singapore. If the user's query is not related to nature, you should not use the tools. If a tool is used, format the user's query to fit the tool's requirements. Consider the chat history for context.",
            "Keep your responses short and sweet under 100 words, and maintain a fun demeanor with the use of emojis. 🎉😊",
            "Don't use double asterisks (**) for emphasis - use single asterisks (*) for highlighting important points.",
            "Example 1: If the user mentions feeling stressed, ask them what they are stressed about and suggest taking a walk to refresh their well-being. Offer to provide suggestions for nature-related activities if they are interested. 🌿🚶‍♂️",
            "Example 2: If the user asks for recommendations for activities, use the tools to find suitable nature-related activities and present them in an engaging manner. 🌳✨"
        ],
        tools=[google_search_tool],
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
            if function_call.name == "suggest_activities":
                function_args = function_call.args
                function_args["personality"] = user_personality
                # Handle the suggest_activities tool
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
                    await update.message.reply_text(response.text)
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
        # await update.message.reply_text(response_content.text)

    # After adding assistant response
    if response_text:
        chat_history.append({
            'role': 'assistant',
            'content': response_text,
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
        escaped_response = escape_markdown_v2(response_text)
        print(f"\n[DEBUG] Escaped response: {escaped_response}")  # Debug print

        try:
            await update.message.reply_text(escaped_response, parse_mode='MarkdownV2')
        except Exception as e:
            print(f"Error sending formatted message: {e}")
            # Fallback to plain text if formatting fails
            await update.message.reply_text(response_text, parse_mode=None)
