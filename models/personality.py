from enum import Enum
from typing import List


class Personality(Enum):
    ADVENTUROUS_ANDY = {
        "name": "Adventurous Andy",
        "traits": [
            "Energetic", "Adventurous", "Outdoor lover", "Lively",
            "Dynamic", "Bold", "Active", "Resilient",
            "Fearless", "Enthusiastic", "Curious", "Nature-loving"
        ],
        "welcome_message": (
            "🏃‍♂️ Perfect choice for an adventure seeker!\n\n"
            "I'm here to help you discover exciting outdoor activities and nature spots in Singapore. "
            "Whether you're looking for hiking trails, water sports, or adrenaline-pumping adventures, "
            "I've got you covered!\n\n"
            "How can I help you start your next adventure today? 🌿🗺️"
        )
    }
    SPONTANEOUS_SAMMY = {
        "name": "Spontaneous Sammy",
        "traits": [
            "Spontaneous", "Independent", "Carefree", "Open-minded",
            "Easygoing", "Flexible", "Free-spirited", "Relaxed",
            "Lay-back"
        ],
        "welcome_message": (
            "🎯 Ah, a free spirit! Love it!\n\n"
            "Ready to discover some spontaneous nature activities? "
            "I can suggest quick getaways and last-minute nature spots that match your flexible style.\n\n"
            "What kind of adventure are you up for today? 🌳✨"
        )
    }
    PLANET_PETE = {
        "name": "Planet Pete",
        "traits": [
            "Compassionate", "Empathetic", "Proactive", "Conscientious",
            "Dedicated", "Protective", "Caring", "Environmental",
            "Committed", "Altruistic"
        ],
        "welcome_message": (
            "🌍 Welcome, fellow earth guardian!\n\n"
            "I'm here to help you connect with nature while protecting our environment. "
            "From eco-friendly activities to conservation efforts, "
            "let's make a positive impact together.\n\n"
            "What environmental interests would you like to explore today? 🌱"
        )
    }
    CHILL_CHARLIE = {
        "name": "Chill Charlie",
        "traits": [
            "Laid-back", "Unhurried", "Peaceful", "Unmotivated",
            "Low-maintenance", "Restful", "Tranquil", "Leisurely",
            "Slow-paced"
        ],
        "welcome_message": (
            "😌 Perfect choice for a relaxed nature lover!\n\n"
            "I know all the peaceful spots and calming nature activities in Singapore. "
            "From quiet gardens to serene water spots, "
            "we'll find your perfect zen moment.\n\n"
            "How would you like to unwind in nature today? 🍃"
        )
    }
    GAMER_GEORGE = {
        "name": "Gamer George",
        "traits": [
            "Competitive", "Strategic", "Tech-savvy", "Immersive",
            "Focused", "Tactical", "Determined", "Analytical",
            "Resourceful", "Problem-solver", "Engaged", "Persistent",
            "Driven", "Quick-thinking"
        ],
        "welcome_message": (
            "🎮 Level up your nature experience!\n\n"
            "I can help you find outdoor activities that match your strategic mindset. "
            "Think of it as a real-world adventure game with achievements to unlock!\n\n"
            "Ready to start your nature quest? What's your first mission? 🎯"
        )
    }
    TRENDY_TIARA = {
        "name": "Trendy Tiara",
        "traits": [
            "Connected", "Inquisitive", "Curious", "Engaged",
            "Trendy", "Observant", "Tech-savvy", "Interactive",
            "Updated", "Explorative", "Entertained", "Informed"
        ],
        "welcome_message": (
            "📱 Welcome to your nature-meets-social journey!\n\n"
            "I'll help you discover Instagram-worthy nature spots and trending outdoor activities. "
            "Let's find the perfect blend of nature and social sharing.\n\n"
            "What kind of trendy nature experience are you looking for today? 🌺"
        )
    }

    @property
    def display_name(self) -> str:
        return self.value["name"]

    @property
    def traits(self) -> List[str]:
        return self.value["traits"]

    @property
    def traits_string(self) -> str:
        return ", ".join(self.traits)

    @property
    def welcome_message(self) -> str:
        return self.value["welcome_message"]

    @classmethod
    def from_display_name(cls, name: str) -> 'Personality':
        for personality in cls:
            if personality.display_name == name:
                return personality
        raise ValueError(f"No personality found with name: {name}")

    @classmethod
    def get_all_display_names(cls) -> List[str]:
        return [p.display_name for p in cls]
