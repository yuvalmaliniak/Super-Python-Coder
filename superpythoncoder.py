# superpythoncoder.py
import random, subprocess, re, time
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style
from tqdm import tqdm
load_dotenv()
client = OpenAI()
PROGRAMS_LIST = [
'''Given two strings str1 and str2, prints all interleavings of the given
two strings. You may assume that all characters in both strings are
different.''',
"a program that checks if a number is a palindrome",
"A program that finds the kth smallest element in a given binary search tree.",
"Given a string s, return the longest palindromic substring in s.",
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
    for attempt in tqdm(range(1, 4), desc=f"{Fore.CYAN}Lint Check Progress{Style.RESET_ALL}", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.YELLOW, Fore.RESET), ncols=80):
        print(f"{Fore.CYAN}Running lint check , Attempt {attempt}...{Style.RESET_ALL}")
        result = subprocess.run(["pylint", file_path], text=True, capture_output=True)
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}Amazing. No lint errors/warnings{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Linting issues detected, trying to fix them..{Style.RESET_ALL}")
            filtered_lint_errors = "\n".join(
                line for line in result.stdout.splitlines() if not line.startswith("*************")
            )       
            conversation_history.append(
                {"role": "assistant", "content": f"The previous code checked was working good is :\n```python\n{current_code}\n```"}
            )
            conversation_history.append(
                {"role": "user", "content": f"The following lint issues were found in the code:\n{filtered_lint_errors}."
                                            f" Please fix these issues while keeping the functionality and logic. Remember to include Code only"}
            )
            current_code = generate_code(conversation_history)
            file_write(current_code)

    print(f"{Fore.RED}There are still lint errors/warnings after 3 attempts.{Style.RESET_ALL}")
    return False

def run_and_optimize_generated_code(clean_code):
    with tqdm(total=100, 
              desc=f"{Fore.CYAN}Code Generation Progress{Style.RESET_ALL}", 
              bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.YELLOW, Fore.RESET), 
              ncols=80) as progress_bar:
        for attempt in range(1, 6):
            progress_bar.update(20)
            progress_bar.refresh()  # Force redraw
            print(f"\n{Fore.CYAN}Attempt {attempt} to run the code{Style.RESET_ALL}")
            start_time = time.time()
            result = subprocess.run(["python", "generatedprogram.py"], capture_output=True, text=True)
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            if result.returncode == 0 and "All tests passed" in result.stdout:  # Check if the script ran successfully (returncode 0 means success)
                print(f"{Fore.GREEN}Code creation completed successfully!{Style.RESET_ALL}")
                subprocess.call(["open", file_path])
                print(f"{Fore.CYAN}Trying to optimize the code for better performance...{Style.RESET_ALL}")
                optimized_run_time = optimize_code(total_time)
                if optimized_run_time:
                    result = subprocess.run(["python", "generatedprogram.py"], capture_output=True, text=True)
                    if result.returncode == 0 and "All tests passed" in result.stdout:
                        print(f"{Fore.GREEN}Code runtime optimization completed successfully, your code runs now in {optimized_run_time} ms instead of {total_time}.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.CYAN}Code optimization failed, but your code is working.{Style.RESET_ALL}")
                        file_write(clean_code) # Write the original code back
                else:
                    print(f"{Fore.CYAN}Code optimization failed, but your code is working.{Style.RESET_ALL}") 
                progress_bar.n = 100  # Manually set progress bar to 100%
                progress_bar.last_print_n = 100
                progress_bar.update(0)  # Force tqdm to redraw with 100%
                return True
            else:  # Handle errors
                combined_output = result.stdout + "\n" + result.stderr
                errors_for_printing = extract_errors_for_user_using_gpt(combined_output)
                errors_for_fix = extract_errors_for_gpt(combined_output)
                if not errors_for_fix:
                    errors_for_fix = errors_for_printing
                print(f"{Fore.RED}Error running generated code! Error: {errors_for_printing}.{Style.RESET_ALL}")
                if (attempt < 5):
                    print(f"{Fore.CYAN}Trying again{Style.RESET_ALL}")
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
    return False

# Program starts here!

print(f'''{Fore.CYAN}I’m Super Python Coder. Tell me, which program would you like me to code for
you? If you don't have an idea,just press enter and I will choose a random
program to code{Style.RESET_ALL}''')

user_program_choice = input()
if not user_program_choice:
    program = random.choice(PROGRAMS_LIST)
    print(f"{Fore.CYAN}Program chosen is: {program}{Style.RESET_ALL}")
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

clean_code = generate_code(conversation_history) # 1st generation
file_write(clean_code) 
run = run_and_optimize_generated_code(clean_code) # Run the code and optimize it's runtime
if (run):
    lint_check() # Check for linting issues
