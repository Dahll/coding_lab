from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier 
from sklearn.tree import DecisionTreeRegressor
from sklearn import tree
from sklearn.tree import _tree
import numpy as np
import os
import configparser
import sys
import contextlib
import openai
import random


USE_STREAM_FEATURE = True
SET_TEMPERATURE_NOISE = False
MAX_TOKENS_DEFAULT = 1000

STREAM = True

def create_template_ini_file(config_path):
    """
  If the ini file does not exist create it and add the organization_id and
  secret_key
  """
    if not os.path.isfile(config_path):
        with open(config_path, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')

        print('OpenAI API config file created at {}'.format(config_path))
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
              'need to register for OpenAI Codex: \n'
              'https://openai.com/blog/openai-codex/')
        sys.exit(1)


def initialize_openai_api(config_path):
    """
  Initialize the OpenAI API
  """
    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file(config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    
    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")


def create_input_prompt(filename, length=3000):
    inputPrompt = ''
    with open(filename) as f:
        #inputPrompt += '# Python to C++: \n'
        inputPrompt += '\n===================\n# Python to C++: \n'
        inputPrompt += '# Python:\n'
        #inputPrompt += '# ' + filename + ':\n'
        inputPrompt += f.read() + '\n'

    inputPrompt = inputPrompt[:length]
    inputPrompt += '\n\n===================\n// ' + 'C++:' + '\n'
    return inputPrompt


def generate_completion(input_prompt, num_tokens):
    temperature = 0.0
    if SET_TEMPERATURE_NOISE:
        temperature += 0.1 * round(random.uniform(-1, 1), 1)
    print("__CODEX: Let me come up with something new ...")
    response = openai.Completion.create(engine='code-davinci-002', prompt=input_prompt, temperature=temperature,
                                        max_tokens=num_tokens, stream=STREAM, stop='===================\n',
                                        top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0)
    return response


def get_generated_response(response):
    generatedFile = "// C++ Code generated from Python Code: \n"
    while True:
        nextResponse = next(response)
        completion = nextResponse['choices'][0]['text']
        generatedFile = generatedFile + completion
        if nextResponse['choices'][0]['finish_reason'] is not None:
            break
    return generatedFile


def write_cpp_file(file_name, textResponse):
    fileName = file_name + ".cpp"
    if os.path.exists(fileName):
        os.remove(fileName)
    f = open(fileName, "a")
    f.write(textResponse)
    f.close()


def test_cpp_compilation(file_name):
    """
  Checks if the generated file is compilable using g++
  """
    
    if os.system("g++ " + file_name + ".cpp" + " -o " + file_name + " &> /dev/null") == 0:
        return True
    else:
        return False


def iterate_for_compilable_solution(file_name, prompt, maxIterations):
    print('Codex is looking for a compilable C++ solution ...')
    for it in range(maxIterations):
        response = generate_completion(prompt, num_tokens=MAX_TOKENS_DEFAULT)
        textResponse = get_generated_response(response)
        write_cpp_file(file_name, textResponse)
        with contextlib.redirect_stdout(None):
            isSolutionCompilable = test_cpp_compilation(file_name)
        if isSolutionCompilable:
            print("Found a compilable solution after {} iterations".format(it+1))
            print("C++ File: {}".format(file_name + ".cpp"))
            print("Compiled Executable: {}".format(file_name))
            break
        if it == maxIterations - 1:
            print('Unfortunately CODEX did not find a compilable solution. Still you can find the generated code '
                  'in the file: {}'.format(file_name + ".cpp"))


def tree_reg_to_code(tree, feature_names, file_name):
    with open(file_name, "w") as f:
        
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]
        #feature_names = [f.replace(" ", "_")[:-5] for f in feature_names]

        input_names = ", ".join(feature_names)

        print(f"def predict({input_names}):", file=f)

        def recurse(node, depth):
            indent = "    " * depth
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                print(f"{indent}if {name} <= {np.round(threshold,2)}:", file=f)
                recurse(tree_.children_left[node], depth + 1)
                print(f"{indent}else:  # if {name} > {np.round(threshold,2)}", file=f)
                recurse(tree_.children_right[node], depth + 1)
            else:
                print(f"{indent}return {np.round(tree_.value[node][0][0], 4)}", file=f)

        recurse(0, 1)
        print("", file=f)
        print("", file=f)
        print("if __name__ == \"__main__\":", file=f)
        print("    print(\"Done\")", file=f)


def decisionTreeReg2cpp(tree, feature_names, output_name, config_path):

    file_name = output_name + ".py"
    
    tree_reg_to_code(tree, feature_names, file_name)

    initialize_openai_api(config_path)
    prompt = create_input_prompt(file_name)
    #print(prompt)
    iterate_for_compilable_solution(output_name, prompt=prompt, maxIterations=3)

