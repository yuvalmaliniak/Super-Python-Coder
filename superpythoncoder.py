import random, subprocess
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
PROGRAMS_LIST = [
'''Given two strings str1 and str2, prints all interleavings of the given
two strings. You may assume that all characters in both strings are
different.Input: str1 = "AB", str2 = "CD"
Output:
ABCD
ACBD
ACDB
CABD
CADB
CDAB
Input: str1 = "AB", str2 = "C"
Output:
ABC
ACB
CAB "''',
"a program that checks if a number is a palindrome",
"A program that finds the kth smallest element in a given binary search tree.",
"A program that checks if euler cycle exists in a given graph",
"A program that checks if a given number is a power of 2"
]
print('''I’m Super Python Coder. Tell me, which program would you like me to code for
you? If you don't have an idea,just press enter and I will choose a random
program to code''')
user_program_choice = input()
if not user_program_choice:
    program = random.choice(PROGRAMS_LIST)
else:
    program = user_program_choice
#print(program)
prompt = f"Create the foolowing python program:{program} .Do not write any explanations, just show me the code itself. Don't add examples that need interact from user, and print your example's output propely."
unit_tests_prompt = """Also please include running unit tests with asserts that check the logic of the
program. Make sure to also check interesting edge cases. There should be at least
10 different unit tests. print how many of the test results passed, and if all tests passed write "All tests passed"."""
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant for code completion. Write only code."},
        {"role": "user", "content": prompt+unit_tests_prompt},
    ]
)
code_content = completion.choices[0].message.content
clean_code = code_content.strip("```").replace("python", "").strip()
file_path = "generatedprogram.py"
with open(file_path, "w") as file:
    file.write(clean_code)
#print("Running the code...")
result = subprocess.run(["python", "generatedcode.py"], capture_output=True)
#print(f"Output: {result.stdout.decode()}")
if "All tests passed" in result.stdout.decode():
    print("Code creation completed successfully !")
    subprocess.call(["open", file_path])
else:
    print("Code creation failed. Please try again.")