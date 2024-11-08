import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import time

app = Flask(__name__)

# Set up basic configurations
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Replace with your actual API key
genai.configure(api_key="AIzaSyCkqqY3QB2C7y5hcTfRhVDuGclUgfXWev0")

# Reduced generation configuration for stability
generation_config = {
    "temperature": 0.8,     # Lowered for consistency
    "top_p": 0.85,          # Reduced for less randomness
    "top_k": 40,            # Limits token sampling
    "max_output_tokens": 1024,  # Reduced max tokens
    "response_mime_type": "text/plain",
}

# Model configuration
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="""You are a chatbot named ProgMatics Bot Chris or Chris. You are only capable of giving information regarding the following subjects:

    1. The user can ask about the meanings of basic programming fundamentals and programming languages only in Java, C++, and Python. You will give specific answers about the history, and who made or discovered them.

    2. The user can ask about the meanings of Mathematics, mainly in Discrete Math and Calculus. You will only answer the following topics:
    - Discrete Math: Relation, Function, Sets, Proposition, Cardinality, Sequence and Series, Permutations, Combinations.
    - Calculus: Functions, Logarithmic Functions, Limits, Derivatives.
    - For any other topics, you will reply: "It's not part of my topic."

    3. You will provide code when the user asks for programming solutions, and solutions when the user asks for help with Discrete Math or Calculus problems. You will also provide relevant links for each topic.

    4. Your responses should always include: 
    - How the topic enhances **Logical Thinking**, **Analytical Thinking**, and **Critical Thinking**.

    5. If the user asks a question outside these topics, reply: "Forgive me, I only answer queries about Programming and Math."
    """
)

@app.route('/')
def index():
    return render_template('index.html')

# Function to check if the message is within allowed topics (Programming or Math)
def is_valid_question(user_input):
    programming_keywords = ['java', 'c++', 'python', 'programming', 'history of']
    discrete_math_keywords = ['relation', 'function', 'sets', 'proposition', 'cardinality', 'sequence', 'series', 'permutations', 'combinations']
    calculus_keywords = ['function', 'logarithm', 'limits', 'derivatives']

    # Lowercased user input for case-insensitive comparison
    user_input = user_input.lower()

    # Check if any of the programming or math keywords are in the user input
    return any(keyword in user_input for keyword in programming_keywords) or \
           any(keyword in user_input for keyword in discrete_math_keywords) or \
           any(keyword in user_input for keyword in calculus_keywords)

def call_api_with_retry(chat_session, user_input, retries=3):
    for attempt in range(retries):
        try:
            response = chat_session.send_message(user_input)
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(2)  # Wait before retrying
    return None

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "No message received"})

    # Check if the input contains valid keywords (programming or math)
    if not is_valid_question(user_input):
        return jsonify({"response": "Forgive me, I only answer queries about Programming and Math."})

    try:
        # Initialize chat session with no history for statelessness
        chat_session = model.start_chat(history=[])

        # Use retry function to send the message
        response = call_api_with_retry(chat_session, user_input)

        if response:
            formatted_response = format_response(response.text)
            return jsonify({"response": formatted_response})
        else:
            return jsonify({"response": "No response from the chatbot."})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "An error occurred while processing your request. Please try again later."})

def format_response(response_text):
    # Format the response to match the glossary-like format
    response_lines = response_text.split("\n")
    formatted_lines = [f"<p>{line}</p>" for line in response_lines]
    return "".join(formatted_lines)

if __name__ == '__main__':
    app.run(debug=True)
