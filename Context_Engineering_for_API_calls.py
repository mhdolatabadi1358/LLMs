#An "LLM-in-the-loop” experiment that tries to auto-write, auto-run, and auto-judge code for a small optimization problem

#pip install openai

import openai
import os
import subprocess

#os.environ['OPENAI_API_KEY'] = "YOUR_OPENAI_API_KEY" # REPLACE WITH YOUR ACTUAL KEY
openai.api_key = os.environ['OPENAI_API_KEY']

import numpy as np

#-------------------------  Create a toy problem: This builds a random 50 × 50 real matrix A and stores it to disk (A.npy).
np.random.seed(47)
n=50;
A = 100*np.random.rand(n, n)-50
np.save('A.npy', A)
#----------------------- The following prompt asks ChatGPT to produce Python that reads A.npy, finds a 0/1 vector x minimising xᵀ A x within 30 seconds, then saves x to x.npy.

prompt = "Develop a Python program to find a binary column vector x (entries are 0 or 1) that minimizes the quadratic form (x^
T)*A*x. The program should read the square matrix A from 'A.npy' using numpy.load() and save the optimal vector x to 'x.npy' using numpy.save(). The entire process must complete within a 30-second time limit. You are allowed exploring optimization techniques (heuristics, exact and hybrid methods) suitable for binary quadratic programming problems, given the time constraint."


for i in range(20):
  #--------------call the OpenAI API with the prompt
  
  response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # You can use other models like "gpt-4", "gpt-4o", etc.
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,  # Adjust temperature for creativity (0.0 for deterministic)
        max_tokens=500,    # Max tokens for the response
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )  
  #------------------------------------ Code Extraction: Extract the Python code from the LLM's as LLM might embed the code within natural language explanations.
  
  generated_code = response.choices[0].message.content.strip()  
  start_delimiter = "```python\n"
  end_delimiter = "```"
  start_index = generated_code.find(start_delimiter)
  if start_index != -1:
    code_start = start_index + len(start_delimiter)
    end_index = generated_code.find(end_delimiter, code_start)
    if end_index != -1:
        generated_code = generated_code[code_start:end_index].strip()
  #print(generated_code)
  
  #------------------------------------- Save the generated code to UBQP.py ----------------------------------------
    
  with open("UBQP.py", "w") as f:
        f.write(generated_code)
    
  #------------------------------------- Executes UBQP.py in a subprocess --------------------------------------------
  
  python_file = 'UBQP.py'
  try:
    result = subprocess.run(["python", python_file], capture_output=True, text=True, check=True)
    if result.stderr=='':
       #print(float(result.stdout))
       print(generated_code)
            
       #-------------------------------- Now that the code runs without any error,  evaluate the generated code's performance simply by printing the calculated objective value   
       x = np.load('x.npy')
       print('optimal objective value for this code=',x.T @ A @ x)  
    else:
       print(result.stderr)
  except subprocess.CalledProcessError as e:
    continue
  except subprocess.TimeoutExpired:
    continue
  except Exception as e:
    continue    
  
  #----------------------------------------------------------------------------------------------------------------



