# enhanced_tutor.py
import aiml
from nltk.tokenize import word_tokenize
import sqlite3
from content_manager import get_content

# Initialize AIML kernel
kernel = aiml.Kernel()
kernel.learn("college-tutor.aiml")
kernel.respond("load aiml b")

# Connect to database
conn = sqlite3.connect('college_tutor.db')
cursor = conn.cursor()

# Keyword mapping to patterns
keyword_patterns = {
    "machine learning": "EXPLAIN MACHINE LEARNING",
    "data structures": "HELP WITH DATA STRUCTURES",
    "job interview": "JOB INTERVIEW TIPS"
}

# Enhanced response function
def get_response(message):
    response = kernel.respond(message)
    if not response:  # No match found
        # Check for keywords
        message_lower = message.lower()
        for keyword, pattern in keyword_patterns.items():
            if keyword in message_lower:
                response = kernel.respond(pattern)
                break
    if "deep dive" in message.lower():
        topic = "machine learning"  # Default topic, expand as needed
        content = get_content(topic)
        response += f" Here's more: {content}"
    elif "example" in message.lower():
        if "python" in message.lower():
            response += " Example: print('Hello, College!')"
    return response if response else "Sorry, I didn’t understand. Try rephrasing or ask about machine learning, data structures, or job interviews!"

# Conversation loop with enhancements
while True:
    message = input("You: ")
    if message.upper() == "QUIT":
        print("Tutor: Goodbye! Feel free to return anytime.")
        break
    response = get_response(message)
    print("Tutor: ", response)

conn.close()