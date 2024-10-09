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
activity_tool = Tool(function_declarations=[suggest_activities_function])
