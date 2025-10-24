"""
AI summarization agent for meeting notes
Connects to local AI server for processing
"""

import requests
import json
from typing import Optional, Dict


class SummarizationAgent:
    """AI agent for summarizing meeting transcriptions"""

    def __init__(self, server_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize summarization agent

        Args:
            server_url: URL of local AI server (Ollama)
            model: Model name to use (llama3, mistral, etc.)
        """
        self.server_url = server_url
        self.model = model
        self.generate_endpoint = f"{server_url}/api/generate"

    def summarize_transcription(self, transcription: str) -> Dict[str, str]:
        """
        Generate summary from meeting transcription

        Args:
            transcription: Raw meeting transcription

        Returns:
            Dict containing summary and extracted info
        """

        prompt = f"""
        Analyze the following meeting transcription and provide:
        1. A concise summary (2-3 sentences)
        2. Key discussion points (bullet points)
        3. Action items (if any)
        4. Fundraising status (if mentioned)
        5. Interest level/sales funnel stage (if applicable)

        Transcription:
        {transcription}

        Provide response in JSON format with keys: summary, key_points, action_items, fundraise, interest
        """

        try:
            response = requests.post(
                self.generate_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')

                # Parse JSON response from model
                try:
                    parsed = json.loads(response_text)
                    return parsed
                except json.JSONDecodeError:
                    # Fallback if model doesn't return valid JSON
                    return {
                        "summary": response_text[:500],
                        "key_points": [],
                        "action_items": [],
                        "fundraise": None,
                        "interest": None
                    }
            else:
                raise Exception(f"AI server error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print("AI server not connected. Using placeholder.")
            return {
                "summary": "[Connect to office AI server for summarization]",
                "key_points": [],
                "action_items": [],
                "fundraise": None,
                "interest": None
            }

        except Exception as e:
            print(f"Summarization error: {e}")
            return {
                "summary": f"[Summarization error: {str(e)}]",
                "key_points": [],
                "action_items": [],
                "fundraise": None,
                "interest": None
            }

    def extract_action_items(self, transcription: str) -> list:
        """
        Extract action items from meeting transcription

        Args:
            transcription: Raw meeting transcription

        Returns:
            List of action items
        """
        prompt = f"""
        Extract all action items and follow-up tasks from this meeting transcription.
        Return as a JSON array of strings.

        Transcription:
        {transcription}
        """

        try:
            response = requests.post(
                self.generate_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')

                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return []

            return []

        except Exception as e:
            print(f"Action item extraction error: {e}")
            return []

    def check_server_status(self) -> bool:
        """Check if AI server is reachable"""
        try:
            response = requests.get(f"{self.server_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


def summarize_meeting(transcription: str, server_url: Optional[str] = None) -> Dict[str, str]:
    """
    Convenience function to summarize meeting

    Args:
        transcription: Meeting transcription text
        server_url: Optional custom server URL

    Returns:
        Summary dict
    """
    agent = SummarizationAgent(server_url=server_url or "http://localhost:11434")
    return agent.summarize_transcription(transcription)


if __name__ == "__main__":
    # Test summarization agent
    agent = SummarizationAgent()

    if agent.check_server_status():
        print("AI server is online!")
    else:
        print("AI server not connected yet.")
        print("Update server URL when your office server is ready.")

    print(f"Server: {agent.server_url}")
    print(f"Model: {agent.model}")
