# superpythoncoder.py
import random, subprocess, re, time
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
PROGRAMS_LIST = [
'''Given two strings str1 and str2, prints all interleavings of the given
two strings. You may assume that all characters in both strings are
different.''',
"a program that checks if a number is a palindrome",
"A program that finds the kth smallest element in a given binary search tree.",
"A program that checks if euler cycle exists in a given graph",
"A program that checks if a given number is a power of 2"
]
file_path = "generatedprogram.py"

def extract_errors_for_user_using_gpt(output):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for code errors. Explain mistakes in the code without suggesting solutions."},
            {"role": "user", "content": f"Please explain the errors via the stdout+stderr we got. Explain only the mistakes in 1 sentence ONLY. Errors: {output}"},
        ]
    )
    return completion.choices[0].message.content

def extract_errors_for_gpt(output):
    pattern = r"AssertionError:.*"
    error_msg = re.search(pattern, output)
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

def optimize_code(total_time):
    with open(file_path, "r") as file:
        previous_code = file.read()
    conversation_history.append(
        {"role": "assistant", "content": f"The previous code that worked good was:\n```python\n{previous_code}\n```"}
    )
    conversation_history.append(
        {"role": "user", "content": f"Please optimize the code for runtime: {program}. Do not change the unit tests, just improve the code runtime. Remember to include only the code."}
    )
    clean_code = generate_code(conversation_history)
    start_time = time.time()
    result = subprocess.run(["python", "generatedprogram.py"], capture_output=True)
    end_time = time.time()
    new_total_time = (end_time - start_time) * 1000
    if (new_total_time < total_time):
        file_write(clean_code)
        return new_total_time
    else:
        return None
def lint_check():
    with open(file_path, "r") as file:
        current_code = file.read()
    for attempt in range(1, 4):
        print(f"Running lint check , Attempt {attempt}...")
        result = subprocess.run(["pylint", file_path], text=True, capture_output=True)
        
        if result.returncode == 0:
            print("Amazing. No lint errors/warnings")
            return True
        else:
            print("Linting issues detected, trying to fix them...")
            filtered_lint_errors = "\n".join(
                line for line in result.stdout.splitlines() if not line.startswith("*************")
            )       
            print(filtered_lint_errors)
            conversation_history.append(
                {"role": "assistant", "content": f"The previous code checked was working good is :\n```python\n{current_code}\n```"}
            )

            conversation_history.append(
                {"role": "user", "content": f"The following lint issues were found in the code:\n{filtered_lint_errors}."
                                            f" Please fix these issues while keeping the functionality and logic. Remember to include Code only"}
            )
            current_code = generate_code(conversation_history)
            file_write(current_code)

    print("There are still lint errors/warnings after 3 attempts.")
    return False

def run_generated_code(clean_code):
    success = False
    runtime_success = False
    attempt = 1
    while attempt <= 5 and not success:
        print(f"Attempt {attempt} to run the code")
        start_time = time.time()
        result = subprocess.run(["python", "generatedprogram.py"], capture_output=True, text=True)
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        if result.returncode == 0 and "All tests passed" in result.stdout:  # Check if the script ran successfully (returncode 0 means success)
            print("Code creation completed successfully !")
            subprocess.call(["open", file_path])
            success = True
            print("Trying to optimize the code for better performance...")
            optimized_run_time = optimize_code(total_time)
            if optimized_run_time:
                result = subprocess.run(["python", "generatedprogram.py"], capture_output=True, text=True)
                if result.returncode == 0 and "All tests passed" in result.stdout:
                    print(f"Code runtime optimization completed successfully, your code runs now in {optimized_run_time} ms instead of {total_time}.")
                else:
                    print("Code optimization failed, but your code is working.")
                    file_write(clean_code) # Write the original code back
            else:
                print("Code optimization failed, but your code is working.") 
        else:  # Handle errors
            combined_output = result.stdout + "\n" + result.stderr
            errors_for_printing = extract_errors_for_user_using_gpt(combined_output)
            errors_for_fix = extract_errors_for_gpt(combined_output)
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
run_generated_code(clean_code)



lint_check()