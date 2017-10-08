import os
import sys
import aiml
import random

if sys.version_info[0] == 3:
    get_text = input
    execute = exec
else:
    get_text = raw_input
    execute = eval

# used constants
caller_fmt = '[{}]: '
bot_str = caller_fmt.format("BOT")
current_session_id = 0
unknown = u"Unknown"
caller = caller_fmt.format(unknown)
sessions = {unknown: current_session_id}

# initialize kernel and paths
kernel = aiml.Kernel()
kernel.setPredicate("name", unknown, current_session_id)
aiml_dir = os.path.join(os.path.dirname(__file__), "aiml")
core_dir = os.path.join(os.path.dirname(__file__), "core")
brain = os.path.join(core_dir, "bot_brain.brn")
if not os.path.exists(core_dir) and not os.path.isdir(core_dir):
    os.makedirs(core_dir)


def init_brain():
    if os.path.isfile(brain):
        kernel.bootstrap(brainFile=brain)
    else:
        # for file_name in os.listdir(aiml_dir):
        #     kernel.learn(os.path.join(aiml_dir, file_name))
        kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
        kernel.saveBrain(brain)


def get_new_session_id(upper_limit=100000):
    sessions_list = sessions.values()
    rand_session = random.randint(1, upper_limit)
    while rand_session in sessions_list:
        rand_session = random.randint(1, upper_limit)
    return rand_session


def aiml_response(text):
    global current_session_id
    return kernel.respond(text, sessions[current_session_id]) \
        if current_session_id else kernel.respond(text)


def get(predicate):
    return kernel.getPredicate(predicate)
    # if not current_session_id else \
    # kernel.getPredicate(predicate, sessionID=current_session_id)


def update_session():
    global caller, caller_fmt
    name = get("name")
    if not name:
        return
    caller = caller_fmt.format(name)
    # if name not in sessions:
    #     sessions[name] = kernel.getSessionData(name)
    # if sessions[name] != current_session_id:
    #     current_session_id = sessions[name]


def process_response(answer):
    """
    Processes response and prints to screen the result
    :param answer: aiml response
    """
    # print(answer)
    print("answer: {} |{}|".format(len(answer), answer))

    text_split = answer.split('|')
    for index in range(len(text_split)):
        # executes everything between `exec(` and `)`
        if text_split[index].startswith('exec('):
            text_split[index] = execute(text_split[index][5:-1])

    answer = "".join(text_split)
    print(bot_str + answer)


if __name__ == '__main__':
    if os.path.exists(brain):
        os.remove(brain)
    init_brain()

    while True:
        message = get_text(caller)
        if message == 'exit':
            exit()
        elif message == 'save':
            kernel.saveBrain(brain)
            print("Brain successfully saved!")
            continue

        response = aiml_response(message)
        if not response:
            print("I didn't catch that. Could you repeat?")
        else:
            update_session()
            process_response(response)
