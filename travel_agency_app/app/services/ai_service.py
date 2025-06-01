import openai # Updated import
from openai import OpenAI # For OpenAI client v1.0.0+
from typing import Optional
import json

from app.schemas.tour import AITourPrompt, AIGeneratedItinerary
from app.core.config import settings

class AIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            # In a real app, you might raise an error or have a fallback
            print("Warning: OPENAI_API_KEY not found. AI service will use mock data or fail.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _construct_prompt_message(self, prompt_data: AITourPrompt) -> str:
        # Basic prompt construction. This can be significantly more sophisticated.
        message = f"""Generate a suggested tour itinerary based on the following details:
Destination: {prompt_data.destination}
Duration (days): {prompt_data.duration_days}
"
        if prompt_data.traveler_type:
            message += f"Traveler Type: {prompt_data.traveler_type}\n"
        if prompt_data.interests:
            message += f"Interests: {', '.join(prompt_data.interests)}\n"
        if prompt_data.budget_level:
            message += f"Budget Level: {prompt_data.budget_level}\n"
        if prompt_data.preferred_activities:
            message += f"Preferred Activities: {', '.join(prompt_data.preferred_activities)}\n"
        message += """
Please provide a suggested tour name, a brief description, a day-by-day itinerary in Markdown format, an estimated price range, and any important warnings or notes for the traveler.

Format your response as a JSON object with the following keys: "tour_name_suggestion", "suggested_description", "itinerary_details" (Markdown string), "estimated_price_range", "warnings" (list of strings).
Example for itinerary_details:
Day 1: Description of activities.\n- Activity 1\n- Activity 2\nDay 2: Description of activities.\n...
"""
        return message

    def generate_itinerary(self, prompt_data: AITourPrompt) -> AIGeneratedItinerary:
        if not self.client:
            # Fallback to mock response if API key is missing
            return self._generate_mock_itinerary(prompt_data)

        full_prompt = self._construct_prompt_message(prompt_data)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful travel assistant that designs tour itineraries and responds in JSON format."
                    },
                    {
                        "role": "user",
                        "content": full_prompt,
                    }
                ],
                model="gpt-3.5-turbo-0125", # Or gpt-4, etc.
                response_format={ "type": "json_object" } # Request JSON output if model supports it
            )

            response_content = chat_completion.choices[0].message.content
            if not response_content:
                raise ValueError("AI response was empty.")

            # Parse the JSON response string from the AI
            ai_response_data = json.loads(response_content)

            return AIGeneratedItinerary(
                tour_name_suggestion=ai_response_data.get("tour_name_suggestion", f"Tour in {prompt_data.destination}"),
                suggested_description=ai_response_data.get("suggested_description", "An amazing tour."),
                itinerary_details=ai_response_data.get("itinerary_details", "No details provided by AI."),
                estimated_price_range=ai_response_data.get("estimated_price_range"),
                warnings=ai_response_data.get("warnings", [])
            )

        except json.JSONDecodeError as e:
            # Handle cases where AI doesn't return valid JSON despite the prompt
            print(f"AI response was not valid JSON: {response_content}. Error: {e}")
            # You could try to extract info from the raw string or return a structured error
            return AIGeneratedItinerary(
                tour_name_suggestion=f"Error: Could not parse AI response for {prompt_data.destination}",
                suggested_description="The AI service returned data in an unexpected format. Please try again or contact support.",
                itinerary_details=f"Raw AI Response (could not parse as JSON):\n{response_content}",
                warnings=["AI response format error."]
            )
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # In a real app, you might want to re-raise a custom exception
            # or return a more user-friendly error structure.
            raise Exception(f"Failed to generate itinerary from AI: {str(e)}")

    def _generate_mock_itinerary(self, prompt_data: AITourPrompt) -> AIGeneratedItinerary:
        # This is the mock response if OPENAI_API_KEY is not set
        mock_itinerary_details = f"""
## Mock Itinerary (OPENAI_API_KEY not set)
Day 1: Arrival in {prompt_data.destination}. Check into hotel. Explore local market.
Day 2: Morning tour of historical sites. Afternoon {prompt_data.interests[0] if prompt_data.interests else 'activity'}.
Day 3: Day trip to nearby attraction. Evening farewell dinner.
Additional days up to {prompt_data.duration_days} will involve more {', '.join(prompt_data.interests) if prompt_data.interests else 'activities'} based on traveler type '{prompt_data.traveler_type if prompt_data.traveler_type else 'any'}' and budget '{prompt_data.budget_level if prompt_data.budget_level else 'any'}'
"""
        return AIGeneratedItinerary(
            tour_name_suggestion=f"Mock {prompt_data.duration_days}-Day Adventure in {prompt_data.destination}",
            suggested_description=f"This is a MOCKED {prompt_data.duration_days}-day tour exploring {prompt_data.destination}. Set OPENAI_API_KEY for real results.",
            itinerary_details=mock_itinerary_details,
            estimated_price_range="$100 - $1000 (mocked)",
            warnings=["This is a MOCKED itinerary. OPENAI_API_KEY is not configured."]
        )
