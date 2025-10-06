import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app) 

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except ValueError as e:
    print(f"Error during Gemini configuration: {e}")
    model = None 

def generate_documentation_prompt(code: str) -> str:
    """
    Creates a detailed, structured prompt for the Google Gemini API to generate code documentation.
    """
    return f"""
    You are an expert technical writer specializing in software documentation. 
    Your task is to analyze the provided code snippet and generate comprehensive, clear, and well-structured documentation.

    Please adhere strictly to the following format. For any section that is not applicable to the given code, write 'N/A'.

    Code Snippet to Document:
    ```
    {code}
    ```

    DOCUMENTATION OUTPUT:

    Project Name:
    (Provide a suitable and concise name for this code snippet.)

    Objective:
    (Clearly describe the primary purpose and goal of the code in one or two sentences.)

    Functions:
    (List and detail each function. Use this format for every function:
    - `functionName(param1_type param1, param2_type param2)`: [Brief description of what the function does.]
      - Parameters:
        - `param1`: [Description of the first parameter.]
        - `param2`: [Description of the second parameter.]
      - Returns: [Description of the return value and its type.])

    Expressions & Algorithms:
    (Explain any complex mathematical calculations, logical expressions, or specific algorithms used in the code. If the logic is straightforward, state that.)

    Features:
    (List the key features or capabilities of the code as bullet points.)

    Use Cases:
    (Describe 2-3 practical, real-world examples or scenarios where this code would be applied. Mention the types of users or systems that would benefit.)

    Sample Test Cases:
    (Provide a few structured test cases to verify the code's functionality. Use this format:
    - Test Case: [Brief description of the test scenario.]
      - Input: [Example input values.]
      - Expected Output: [The expected result for the given input.])

    Overall Flow:
    (Provide a high-level, step-by-step description of the program's execution flow from start to finish.)
    """

@app.route('/generate-docs', methods=['POST'])
def generate_docs():
    """
    Flask endpoint to receive code, generate documentation via Gemini, and return it.
    """
    if not model:
        return jsonify({"error": "Google Gemini client is not configured. Please set the GOOGLE_API_KEY environment variable."}), 500

    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "No code provided in the request."}), 400
    
    user_code = data['code']
    if not user_code.strip():
        return jsonify({"error": "Code cannot be empty."}), 400
    
    try:
        prompt_text = generate_documentation_prompt(user_code)
        response = model.generate_content(prompt_text)

        generated_docs = response.text

        return jsonify({"documentation": generated_docs})

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_message = f"An error occurred while communicating with the Gemini API: {str(e)}"
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)


