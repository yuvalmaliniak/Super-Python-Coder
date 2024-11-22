# chatgpt_competion.py
# Description: This file contains the code for the competition of the ChatGPT model.
from openai import OpenAI
client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant for code completion. Write only code."},
        {"role": "user", "content": "“Create a python program that checks if a number is even and divided by 9. Do not write any explanations, just show me the code itself."},
    ]
)
print(completion.choices[0].message['content'])
