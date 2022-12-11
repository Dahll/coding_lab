from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier 
from sklearn.tree import DecisionTreeRegressor
from sklearn import tree
from sklearn.tree import _tree
from datetime import datetime
import numpy as np
import os
import configparser
import sys
import contextlib
import openai
import random


def test_cpp_compilation(file_name):
    """
  Checks if the generated file is compilable using g++
  """
    
    if os.system("g++ " + file_name + ".cpp" + " -o " + file_name + " &> /dev/null") == 0:
        return True
    else:
        return False


def add_main(file_name):
    with open(file_name, "a") as f:
        print("", file=f)
        print("", file=f)
        print("if __name__ == \"__main__\":", file=f)
        print("    print(\"Done\")", file=f)


def tree_reg_to_code(tree, feature_names, file_name, function_name, mode="w"):
    with open(file_name, mode) as f:
        
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]

        input_names = ", ".join(feature_names)

        print(f"def {function_name}({input_names}):", file=f)

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


def gen_random_forest(names, features_names, file_name):
    with open(file_name, "a") as f:
        input_names = ", ".join(features_names)
        indent = "    "
        print(f"def random_forest_evaluation({input_names}):", file=f)
        print(f"{indent}score = 0", file=f)
        for name in names:
            print(f"{indent}score += {name}({input_names})", file=f)
        print(f"{indent}score /= {len(names)}", file=f)
        print(f"{indent}return score", file=f)


def random_forest_reg_to_code(model, features_names, file_name):
    
    trees = model.estimators_
    names = ["predict_0"]
    tree_reg_to_code(trees[0], features_names, file_name, "predict_0",mode="w")
    for i in range(1, len(trees) - 1):
        tree_reg_to_code(trees[i], features_names, file_name, "predict_" + str(i), mode="a")
        names.append("predict_" + str(i))
    tree_reg_to_code(trees[len(trees)-1], features_names, file_name, "predict_" + str(len(trees)-1), mode="a")
    names.append("predict_" + str(len(trees)-1))
    
    gen_random_forest(names, features_names, file_name)
    
    add_main(file_name)


def addMain2cpp(file_name):
    with open(file_name, "a") as f:
        print("", file=f)
        print("", file=f)
        print("int main(int argc, char *argv[])", file=f)
        print("{", file=f)
        print("    std::cout << random_forest_evaluation(0, 0, 0, 0) << std::endl;", file=f)
        print("}", file=f)


def decisionTreePredict2cpp(tree, feature_names, file_name, function_name, mode="w"):
    with open(file_name, mode) as f:
        
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]

        input_names = "float " + ", float ".join(feature_names)

        print(f"float {function_name}({input_names})", file=f)
        print("{", file=f)
        def recurse(node, depth):
            indent = "    " * depth
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                print(f"{indent}if ({name} <= {np.round(threshold,2)})", file=f)
                
                print(f"{indent}{{", file=f)
                
                recurse(tree_.children_left[node], depth + 1)
                print(f"{indent}}}", file=f)
                print(f"{indent}else", file=f)
                print(f"{indent}{{", file=f)
                recurse(tree_.children_right[node], depth + 1)
                print(f"{indent}}}", file=f)
            else:
                print(f"{indent}return {np.round(tree_.value[node][0][0], 4)};", file=f)

        recurse(0, 1)
        print("}", file=f)


def randomForestMean2code(names, features_names, file_name):
    with open(file_name, "a") as f:
        input_names = "float " + ", float ".join(features_names)
        input_var = ", ".join(features_names)
        indent = "    "
        print(f"float random_forest_evaluation({input_names})", file=f)
        print("{", file=f)
        print(f"{indent}float score = 0;", file=f)
        for name in names:
            print(f"{indent}score += {name}({input_var});", file=f)
        print(f"{indent}score /= {len(names)};", file=f)
        print(f"{indent}return score;", file=f)
        print("}", file=f)


def headerAndLib(file_name):
    with open(file_name, "w") as f:
        print("#include <iostream>", file=f)
        
def randomForestPredict2code(model, features_names, file_name):
    
    headerAndLib(file_name)
    names = []
    trees = model.estimators_
    for i in range(len(trees)):
        decisionTreePredict2cpp(trees[i], features_names, file_name, "predict_" + str(i), mode="a")
        names.append("predict_" + str(i))
    
    randomForestMean2code(names, features_names, file_name)
    
    #addMain2cpp(file_name)


def convertRandomForest(model, feature_names, file_name):

    random_forest_reg_to_code(model, feature_names, file_name + ".py")

    randomForestPredict2code(model, feature_names, file_name + ".cpp")

    #test_cpp_compilation(file_name)


def mergeCppFiles(path_main, path_eval, path_output):
    with open(path_main, "r") as f:
        string_main = f.read()
    
    with open(path_eval, "r") as f:
        string_eval = f.read()
    
    with open(path_output, "w") as f:
        f.write(string_eval)
        f.write(string_main)


def compileCppFiles(input_name, exec_name):
    """
  Checks if the generated file is compilable using g++
  """

    if os.system("g++ " + input_name + " -o " + exec_name + " &> /dev/null") == 0:
        return True
    else:
        return False


def generate_agent(model, feature_names, path_main, rep_eval="../data/eval/", rep_agent_cpp="../data/agent/", rep_agent_bin="../data/binary/"):
    
    now = datetime.now()
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")
    
    name = path_main.split("/")[-1].split(".")[0] + "_" + dt_string
    
    convertRandomForest(model, feature_names, rep_eval + "eval_" + name)
    mergeCppFiles(path_main, rep_eval + "eval_" + name + ".cpp", rep_agent_cpp + "agent_" + name + ".cpp")
    compileCppFiles(rep_agent_cpp + "agent_" + name + ".cpp", rep_agent_bin + "bin_" + name)


