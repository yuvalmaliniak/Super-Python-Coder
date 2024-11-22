# chatgpt_competion.py
# Description: This file contains the code for the competition of the ChatGPT model.

from dotenv import load_dotenv
load_dotenv()
import subprocess
from openai import OpenAI
client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant for code completion. Write only code."},
        {"role": "user", "content": "“Create a python program that checks if a number is even and divided by 9. Do not write any explanations, just show me the code itself. Don't add examples that need interact from user, and print your example's output propely."},
    ]
)
code_content = completion.choices[0].message.content
clean_code = code_content.strip("```").replace("python", "").strip()
#print(clean_code)
with open("generatedcode.py", "w") as file:
    file.write(clean_code)
print("Code has been written to generatedcode.py")
print("Running the code...")
result = subprocess.run(["python", "generatedcode.py"], capture_output=True)
print(f"Output: {result.stdout.decode()}")