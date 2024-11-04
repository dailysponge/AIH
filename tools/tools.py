from vertexai.generative_models import GenerativeModel, FunctionDeclaration, Tool


suggest_activities_function = FunctionDeclaration(
    name="suggest_activities",
    description="Suggest some nature activities based on user's personality to promote nature connectedness.",
    parameters={
        "type": "object",
        "properties": {
            "personality": {
                "type": "string",
                "description": "The personality type of the user."
            }
        }
    },
)

google_search_function = FunctionDeclaration(
    name="question_answer_tool",
    description="Retrieves the answer to the user's query in Singapore context. The output should be nature related, brief, easy to read with bullet points and contains emojis to make it more engaging.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to be performed."
            },
        }
    },
)
google_search_tool = Tool(
    function_declarations=[google_search_function],
)

activity_tool = Tool(
    function_declarations=[suggest_activities_function],
)

feedback_function = FunctionDeclaration(
    name="handle_feedback",
    description="Process user feedback about suggested activities and check if activities were completed.",
    parameters={
        "type": "object",
        "properties": {
            "is_feedback": {
                "type": "boolean",
                "description": "Whether the user's message appears to be feedback about a suggested activity."
            },
        }
    },
)

feedback_tool = Tool(
    function_declarations=[feedback_function],
)
