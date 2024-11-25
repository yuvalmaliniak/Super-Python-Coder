# superpythoncoder.py
import random, subprocess, re, time
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
file_path = "generatedprogram.py"

def extract_errors_for_user_using_gpt(stderr):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for code errors. Explain mistakes in the code without suggesting solutions."},
            {"role": "user", "content": f"Please explain the errors via the errors we got. Explain only the mistakes in 1 sentence ONLY. Errors: {stderr}"},
            {"role": "user", "content": unit_tests_expanded}
        ]
    )
    return completion.choices[0].message.content

def extract_errors_for_gpt(stderr):
    pattern = r"AssertionError:.*"
    error_msg = re.search(pattern, stderr)
    if error_msg:
        return error_msg.group(0)
    else:
        return None
    
def generate_code(messages):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    response_content = completion.choices[0].message.content
    cleaned_code = response_content.replace("```python", "").replace("```", "").strip()
    return cleaned_code

def file_write(clean_code):
    with open(file_path, "w") as file:
        file.write(clean_code)
# Start the program
print('''I’m Super Python Coder. Tell me, which program would you like me to code for
you? If you don't have an idea,just press enter and I will choose a random
program to code''')

user_program_choice = input()
if not user_program_choice:
    program = random.choice(PROGRAMS_LIST)
    print("Program chosen is:", program)
else:
    program = user_program_choice

prompt = f"Create the following python program:{program} .Do not write any explanations, just show me the code itself. Don't add examples that need interact from user, and print your example's output propely."
unit_tests_prompt = """Also please include running unit tests (USE asserts) that check the logic of the
program. Make sure to also check interesting edge cases. There should be at least
10 different unit tests. Use for loops to number the assertions, so when a failure occur the user can see which test failed."""
unit_tests_expanded = """If all tests passed write "All tests passed".
If some tests didn't pass, print for each test the Input ,Output and the Expected output."""
conversation_history = [
        {"role": "system", "content": "You are a helpful assistant for code completion. Write only code."},
        {"role": "user", "content": prompt+unit_tests_prompt},
        {"role": "user", "content": unit_tests_expanded}]

clean_code = generate_code(conversation_history)
file_write(clean_code)
# Run code up to 5 times if it fails
success = False
attempt = 1
while attempt <= 5 and not success:
    print(f"Attempt {attempt} to run the code")
    start_time = time.time()
    result = subprocess.run(["python", "generatedprogram.py"], capture_output=True)
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    if result.returncode == 0 and "All tests passed" in result.stdout.decode():  # Check if the script ran successfully (returncode 0 means success)
        print("Code creation completed successfully !")
        success = True
        subprocess.call(["open", file_path])
        break
    else:  # Handle errors
        errors_for_printing = extract_errors_for_user_using_gpt(result.stderr.decode())
        errors_for_fix = extract_errors_for_gpt(result.stderr.decode())
        if not errors_for_fix:
            errors_for_fix = errors_for_printing
        print(f"Error running generated code! Error: {errors_for_printing}.")
        if (attempt < 5):
            print("Trying again")
        conversation_history.append(
            {"role": "assistant", "content": f"The previous code generated was:\n```python\n{clean_code}\n```"}
            )
        conversation_history.append(
            {"role": "user", "content": f"The previous code had the following errors: {errors_for_fix}. "
                                        f"Error summary is {errors_for_printing}"
                                        f"Please fix the issues and regenerate the program: {program}. Remember to include only the code."}
        )
        clean_code = generate_code(conversation_history)
        attempt += 1
        file_write(clean_code)
    if (attempt > 5):
        print("Code generation FAILED.")
if (success):
    #Optimizing runtime
    print("Optimizing code run time")
    conversation_history.append(
        {"role": "assistant", "content": f"The previous code that worked good was:\n```python\n{clean_code}\n```" 
        }                                
    )
    conversation_history.append(
        {"role": "user", "content": f"Please optimize the code for runtime: {program}. Do not change the unit tests, just improve the code runtime. Remember to include only the code."}
    )
    clean_code = generate_code(conversation_history)
    file_write(clean_code)
    start_time = time.time()
    result = subprocess.run(["python", "generatedprogram.py"], capture_output=True)
    end_time = time.time()
    new_total_time = (end_time - start_time) * 1000
    if (new_total_time < total_time):
        print(f"Code running time optimized! It now runs in {new_total_time} milliseconds, while before it was {total_time} milliseconds")
        subprocess.call(["open", file_path])