import json
import sys
from copy import deepcopy
import os
from art import *

args = sys.argv
path = ""
full_data = ""
temp_data = {"beliefs": [], "actions": []}
last_code = ""
Art=text2art("Dialog Annotator")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_dialog(code):
    if code.strip() in full_data:
        global last_code
        last_code = code
        current_dialog = full_data[code]
        return current_dialog
    else:
        dialog_code = input('No dialog found, pleas insert valid dialog code\n')
        return get_dialog(dialog_code)


def build_belief_data(data):
    o = {}
    for v in range(len(data)):
        if v == 1:
            o["prev_bs"] = data[-1]
        if v == 2:
            o["user_nlu"] = data[1]
        if v == 3:
            o["prev_act"] = data[3]
        if v == 4:
            o["out_bs"] = data[2]

    return o

def build_action_data(data):
    o = {}
    for v in range(len(data)):
        if v == 1:
            o["prev_act"] = data[-1]
        if v == 2:
            o["curr_bs"] = data[1]
        if v == 3:
            o["user_nlu"] = data[2]
        if v == 4:
            o["match"] = data[3]
        if v == 5:
            o["pointer"] = data[4]
        if v == 6:
            o["out_act"] = data[5]

    return o


def choise_belief(options):
    d = deepcopy(options)
    print(f'{bcolors.WARNING}{5 * "*"}  BELIEF RULE {5 * "*"}{bcolors.ENDC}')
    i = input(f'{bcolors.BOLD}If you want edit one of the following values, press Enter if you want confirm{bcolors.ENDC}\n\n'
              f'{bcolors.BOLD}text:"{d[1]}"{bcolors.ENDC}\n'
              f'{bcolors.BOLD}resp:"{d[0]}"{bcolors.ENDC}\n\n'
              f'[0] user_nlu:"{d[2]}"\n'
              f'[1] belief:"{d[3]}"\n'
              f'[2] sys_act:"{d[4]}"\n'
              f'{20 * "*"}\n')
    if len(i.strip()) > 0:
        o = input_with_default("Type new value\n\n", d[int(i) + 2])
        d[int(i) + 2] = o
        return choise_belief(d)
    else:
        return d


def choise_action(options):
    d = deepcopy(options)
    print(f'{bcolors.WARNING}{5 * "*"}  ACTION RULE {5 * "*"}{bcolors.ENDC}')

    i = input(f'{bcolors.BOLD}If you want edit one of the following values, press Enter if you want confirm{bcolors.ENDC}\n\n'
              f'{bcolors.BOLD}text:"{d[1]}"{bcolors.ENDC}\n'
              f'{bcolors.BOLD}resp:"{d[0]}"{bcolors.ENDC}\n\n'
              f'[0] curr_bs:"{d[2]}"\n'
              f'[1] user_nlu:"{d[3]}"\n'
              f'[2] pointer:"{d[4]}"\n'
              f'[3] match:"{d[5]}"\n'
              f'[4] out_act:"{d[6]}"\n'
              f'[5] prev_act:"{d[7]}"\n'
              f'{20 * "*"}\n')
    if len(i.strip()) > 0:
        o = input_with_default("Type new value\n\n", d[int(i) + 2])
        d[int(i) + 2] = o
        return choise_action(d)
    else:
        return d

def insert_dialog_code():
    dialog_code = input('Insert dialog code\n')
    try:
        dialog = get_dialog(dialog_code)
        log = dialog["log"]
        d_index = 0
        global temp_data
        for turn in log:
            print(f'{bcolors.WARNING}{5 * "*"} Turn {d_index} {5 * "*"}{bcolors.ENDC}')
            text = turn["user"]
            nlu = turn["user_nlu"]
            belief = turn["constraint"]
            sys_act = turn["sys_act"]
            ######
            curr_bs = turn["constraint"]
            nlu_act = nlu
            match = turn["match"]
            pointer = turn["pointer"]
            out_act = turn["sys_act"]
            resp = turn["resp"]

            data_belief = [resp,text, nlu, belief, sys_act]
            data_action = [resp,text,curr_bs,nlu_act,match,pointer,out_act]

            if d_index == 0:
                data_belief.append("")
                data_action.append("[general] [welcome]")
            else:
                data_belief.append(temp_data["beliefs"][d_index-1]["out_bs"])
                data_action.append(temp_data["actions"][d_index-1]["out_act"])

            b = choise_belief(data_belief)
            a = choise_action(data_action)
            temp_data["beliefs"].append(build_belief_data(b))
            temp_data["actions"].append(build_action_data(a))
            d_index += 1
    except Exception as e:
        print("Error, try again")
        print(e)



def input_with_default(prompt, prefill=''):
    try:
        from pyautogui import typewrite
        print(prompt)
        typewrite(prefill)
        return input()
    except (ImportError, KeyError):
        import readline
        readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def save(code):
    if not os.path.exists("./annotated"):
        os.makedirs("./annotated")
    output = open(f"./annotated/{code}_annotation.json", "w+")
    json.dump(temp_data, output)
    output.close()
    print(f'{bcolors.OKBLUE}Rules saved in ./annotated/{code}_annotation.json{bcolors.ENDC}')


def ask_continue():

    continue_t = input(f"{bcolors.OKGREEN}Dialog is finished, type E to exit or C to continue with the next dialog\n{bcolors.ENDC}")

    save(last_code)
    if continue_t == "E":
        exit(0)
    else:
        insert_dialog_code()
        ask_continue()


for index in range(len(args)):
    if args[index] == "-path" or args[index] == "-p":
        path = args[index + 1]
print(Art)
print("\n\n\n")

data_file = open(path, "r+")
full_data = json.load(data_file)

insert_dialog_code()
ask_continue()
