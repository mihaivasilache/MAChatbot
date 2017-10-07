import os
import aiml
import random

current_session_id = 0
sessions = {"Unknown": 0}

kernel = aiml.Kernel()
aiml_dir = os.path.join(os.path.dirname(__file__), "aiml")
core_dir = os.path.join(os.path.dirname(__file__), "core")
brain = os.path.join(core_dir, "bot_brain.brn")
if not os.path.exists(core_dir) and not os.path.isdir(core_dir):
    os.makedirs(core_dir)


def init_brain():
    if os.path.isfile(brain):
        kernel.bootstrap(brainFile=brain)
    else:
        for file_name in os.listdir(aiml_dir):
            kernel.learn(os.path.join(aiml_dir, file_name))
        kernel.saveBrain(brain)


def get_new_session_id(upper_limit=100000):
    sessions_list = sessions.values()
    rand_session = random.randint(1, upper_limit)
    while rand_session in sessions_list:
        rand_session = random.randint(1, upper_limit)
    return rand_session


def aiml_response(text):
    return kernel.respond(text)


def get(predicate):
    return kernel.getPredicate(predicate) if not current_session_id else \
        kernel.getPredicate(predicate, sessionID=current_session_id)


def update_session():
    global current_session_id
    name = get("name")
    if not name:
        name = "Unknown"
    if sessions[name] != current_session_id:
        if name not in sessions:
            sessions[name] = get_new_session_id()
        current_session_id = sessions[name]

if os.path.exists(brain):
    os.remove(brain)
init_brain()

while True:
    message = raw_input('[BOT CHAT]: ')
    if message == 'exit':
        exit()
    elif message == 'save':
        kernel.saveBrain(brain)
        print("Brain successfully saved!")
        continue

    response = aiml_response(message)
    if "WARNING: No match found for input: " in response:
        print("I didn't catch that. Could you repeat?")
    else:
        print(response)
