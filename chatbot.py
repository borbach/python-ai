import random
import re

class SimpleChatbot:
    def __init__(self):
        self.name = "ChatBot"
        self.responses = {
            'greeting': [
                "Hello! How are you today?",
                "Hi there! Nice to meet you!",
                "Hey! What's on your mind?",
                "Greetings! How can I help you?"
            ],
            'how_are_you': [
                "I'm doing well, thank you for asking!",
                "I'm great! How about you?",
                "I'm functioning perfectly! What about you?",
                "All systems running smoothly here!"
            ],
            'name': [
                f"My name is {self.name}. What's yours?",
                f"I'm {self.name}! Nice to meet you!",
                f"You can call me {self.name}. And you are?",
                f"I go by {self.name}. What should I call you?"
            ],
            'weather': [
                "I don't have access to weather data, but I hope it's nice where you are!",
                "I can't check the weather, but is it a beautiful day where you are?",
                "Weather talk! I wish I could see outside. How's it looking?"
            ],
            'goodbye': [
                "Goodbye! It was nice chatting with you!",
                "See you later! Have a great day!",
                "Farewell! Thanks for the conversation!",
                "Bye! Come back anytime!"
            ],
            'default': [
                "That's interesting! Tell me more.",
                "I see. What else is on your mind?",
                "Hmm, can you elaborate on that?",
                "That's cool! What do you think about it?",
                "I hear you. Anything else you'd like to talk about?",
                "Interesting perspective! What made you think of that?",
                "I'm listening. Please continue.",
                "That sounds fascinating! Can you share more details?"
            ]
        }
        
        self.patterns = {
            r'\b(hi|hello|hey|greetings)\b': 'greeting',
            r'\b(how are you|how\'re you|how are ya)\b': 'how_are_you',
            r'\b(what\'s your name|who are you|your name)\b': 'name',
            r'\b(weather|sunny|rainy|cloudy|hot|cold)\b': 'weather',
            r'\b(bye|goodbye|see ya|farewell|exit|quit)\b': 'goodbye'
        }
    
    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        
        # Check if user wants to exit
        if user_input in ['exit', 'quit', 'bye', 'goodbye']:
            return random.choice(self.responses['goodbye']), True
        
        # Match patterns
        for pattern, response_type in self.patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                return random.choice(self.responses[response_type]), False
        
        # Default response
        return random.choice(self.responses['default']), False
    
    def chat(self):
        print(f"🤖 {self.name}: Hello! I'm a simple chatbot. Let's have a conversation!")
        print(f"🤖 {self.name}: Type 'exit' when you want to end our chat.\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    print(f"🤖 {self.name}: I didn't catch that. Could you say something?\n")
                    continue
                
                response, should_exit = self.get_response(user_input)
                print(f"🤖 {self.name}: {response}\n")
                
                if should_exit:
                    break
                    
            except KeyboardInterrupt:
                print(f"\n🤖 {self.name}: Goodbye! Thanks for chatting!")
                break
            except EOFError:
                print(f"\n🤖 {self.name}: It looks like you left. Goodbye!")
                break

def main():
    chatbot = SimpleChatbot()
    chatbot.chat()

if __name__ == "__main__":
    main()


