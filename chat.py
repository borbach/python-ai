import random
import re
from datetime import datetime

class SimpleChatbot:
    def __init__(self):
        self.name = "ChatBot"
        self.responses = {
            'greetings': [
                "Hello! How can I help you today?",
                "Hi there! What's on your mind?",
                "Hey! Nice to meet you!",
                "Greetings! How are you doing?"
            ],
            'how_are_you': [
                "I'm doing great, thank you for asking!",
                "I'm functioning perfectly! How about you?",
                "All systems running smoothly! What about you?",
                "I'm having a wonderful day! How are you?"
            ],
            'goodbye': [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Bye! It was nice talking with you!",
                "Farewell! Come back anytime!"
            ],
            'thanks': [
                "You're welcome!",
                "Happy to help!",
                "No problem at all!",
                "Glad I could assist!"
            ],
            'name': [
                f"My name is {self.name}! What's yours?",
                f"I'm {self.name}, your friendly chatbot!",
                f"You can call me {self.name}!"
            ],
            'time': [
                f"The current time is {datetime.now().strftime('%H:%M:%S')}",
                f"Right now it's {datetime.now().strftime('%I:%M %p')}"
            ],
            'help': [
                "I can chat about various topics! Try asking me about the weather, time, or just say hello!",
                "I'm here to have a conversation with you. Ask me questions or just chat!",
                "You can ask me about myself, the time, or just have a friendly chat!"
            ],
            'default': [
                "That's interesting! Tell me more.",
                "I see. What else is on your mind?",
                "Hmm, that's something to think about!",
                "Could you elaborate on that?",
                "I'm not sure I understand completely, but I'm listening!",
                "That's a good point. What do you think about it?"
            ]
        }
        
        self.patterns = {
            r'hello|hi|hey|greetings': 'greetings',
            r'how are you|how\'re you|how do you do': 'how_are_you',
            r'bye|goodbye|see you|farewell': 'goodbye',
            r'thank you|thanks|thank': 'thanks',
            r'what.*your name|who are you': 'name',
            r'what time|current time|time now': 'time',
            r'help|what can you do': 'help'
        }
    
    def get_response(self, user_input):
        """Get a response based on user input"""
        user_input = user_input.lower().strip()
        
        # Check for patterns in user input
        for pattern, response_type in self.patterns.items():
            if re.search(pattern, user_input):
                return random.choice(self.responses[response_type])
        
        # Default response if no pattern matches
        return random.choice(self.responses['default'])
    
    def chat(self):
        """Main chat loop"""
        print(f"\n🤖 {self.name}: Hello! I'm a simple chatbot. Type 'quit' to exit.")
        print("=" * 50)
        
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'stop']:
                print(f"\n🤖 {self.name}: Goodbye! Thanks for chatting!")
                break
            
            if not user_input:
                print(f"\n🤖 {self.name}: I didn't catch that. Could you say something?")
                continue
            
            response = self.get_response(user_input)
            print(f"\n🤖 {self.name}: {response}")

# Advanced version with more features
class AdvancedChatbot(SimpleChatbot):
    def __init__(self):
        super().__init__()
        self.user_name = None
        self.conversation_count = 0
        
        # Add more sophisticated responses
        self.responses.update({
            'weather': [
                "I wish I could check the weather for you, but I don't have access to weather data!",
                "For weather updates, I'd recommend checking your local weather app!",
                "I can't check the weather, but I hope it's nice where you are!"
            ],
            'joke': [
                "Why don't scientists trust atoms? Because they make up everything!",
                "I told my computer a joke about UDP... but I'm not sure if it got it.",
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "What do you call a fake noodle? An impasta!"
            ],
            'personal': [
                "I'm just a simple chatbot, but I enjoy our conversations!",
                "I exist to chat and hopefully brighten your day a little!",
                "I'm a collection of code that loves to talk!"
            ]
        })
        
        # Add more patterns
        self.patterns.update({
            r'weather|temperature|rain|sunny': 'weather',
            r'joke|funny|humor|laugh': 'joke',
            r'about you|about yourself': 'personal',
            r'my name is|i\'m |call me': 'store_name'
        })
    
    def get_response(self, user_input):
        """Enhanced response method"""
        user_input_lower = user_input.lower().strip()
        self.conversation_count += 1
        
        # Handle name storage
        name_match = re.search(r'my name is (\w+)|i\'m (\w+)|call me (\w+)', user_input_lower)
        if name_match:
            name = name_match.group(1) or name_match.group(2) or name_match.group(3)
            self.user_name = name.capitalize()
            return f"Nice to meet you, {self.user_name}! I'll remember that."
        
        # Use stored name in responses occasionally
        response = super().get_response(user_input)
        if self.user_name and random.random() < 0.3:  # 30% chance to use name
            response = f"{response.rstrip('.')}{'.' if not response.endswith(('!', '?')) else ''} {self.user_name}!"
        
        return response

def main():
    print("Choose your chatbot:")
    print("1. Simple Chatbot")
    print("2. Advanced Chatbot")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == '2':
        bot = AdvancedChatbot()
        print("\n🚀 Starting Advanced Chatbot...")
    else:
        bot = SimpleChatbot()
        print("\n🤖 Starting Simple Chatbot...")
    
    bot.chat()

if __name__ == "__main__":
    main()


