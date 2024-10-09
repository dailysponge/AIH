from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from vertexai.generative_models import GenerativeModel, Part, Content
from tools.tools import activity_tool
from google.cloud import aiplatform
aiplatform.init(project="aihsmu")

model = model = GenerativeModel(
    "gemini-1.0-pro",
    system_instruction=[
        "Your task is to help users with their nature related activities.",
    ],
    tools=[activity_tool],
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message and prompt for the personality quiz."""
    print("start")
    user = update.effective_user
    user_personality = "adventurous"
    user_prompt_content = Content(
        role="user",
        parts=[
            Part.from_text(
                f"Im quite {user_personality} and looking for some nature activities"),
        ],
    )
    res = model.generate_content(
        user_prompt_content,
        tools=[activity_tool]
    )
    function_call = res.candidates[0].function_calls[0]
    print('func_call', function_call)
    print("this is res", res)
    response = model.generate_content(
        [
            user_prompt_content,
            res.candidates[0].content,
            Content(
                parts=[
                    Part.from_function_response(
                        name=function_call.name,
                        response={
                            "personality": function_call.args,
                        },
                    ),
                ]
            )
        ]
    )
    print("THIS IS final RES",  response.text)
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n"
        "Welcome to the Nature Connect Bot.\n"
        "Please take our personality quiz here: [Personality Quiz](https://your-quiz-link.com)\n"
        "After completing, type /activities to get personalized suggestions.",
        parse_mode='Markdown'
    )
