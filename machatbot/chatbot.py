# python 2 and 3 compatibility imports
from __future__ import absolute_import, print_function, division, unicode_literals
from six import exec_

import os
import sys
import aiml
import json
import time
import random
import threading


if sys.version_info[0] == 3:
    get_text = input
else:
    get_text = raw_input

# used constants
caller_fmt = '[{}]:\t'
bot_str = caller_fmt.format("BOT")
current_session_id = 0
unknown = u"Unknown"
caller = caller_fmt.format(unknown)
sessions = {unknown: current_session_id}

daemons = []

# import aiml files
to_be_imported = {
    "alice": [
        "personality", "psychology", "salutations", "stories",
        "science", "religion", "money", "history"
    ],
    "standard": ["std-that"]
}

# users
users = dict()
current_user = unknown
last_chat_time = time.time()
delay = 15

age_fmt = "AGE BETWEEN {} AND {}"
limits = [[0, 26, 65], [25, 64, 100]]

# initialize kernel and paths
kernel = aiml.Kernel()
kernel.setPredicate("name", unknown, current_session_id)
aiml_dir = os.path.join(os.path.dirname(__file__), "aiml")
core_dir = os.path.join(os.path.dirname(__file__), "core")
users_file = os.path.join(core_dir, "users")
brain = os.path.join(core_dir, "bot_brain.brn")
if not os.path.exists(core_dir) and not os.path.isdir(core_dir):
    os.makedirs(core_dir)


def import_bot_data(file_name=None, bot=None, all_files=False):
    """
    Loads aiml file and learns from it
    :param file_name: the file name from the predefined aiml files from python-aiml
    :param bot: can be either "alice" or "standard"
    :param all_files: if its True it will import all files from bot
    """
    if not file_name and not bot or not bot and not all_files:
        raise ValueError("No bot or file given")
    if file_name:
        if not file_name.endswith(".aiml"):
            file_name += ".aiml"
    if bot:
        bot = bot.lower()
        if bot not in ["alice", "standard"]:
            raise NameError("Unavailable bot data found")
    file_path = file_name
    if bot and isinstance(bot, str):
        file_path = os.path.join(bot, file_path) if file_path else bot
    file_path = os.path.join(aiml.__path__[0], 'botdata', file_path)
    if not all_files:
        kernel.learn(file_path)
    else:
        kernel.bootstrap(learnFiles="startup.xml", commands="load {}".format(bot),
                         chdir=file_path)


def init_brain():
    if os.path.isfile(brain):
        kernel.bootstrap(brainFile=brain)
    else:
        # for file_name in os.listdir(aiml_dir):
        #     kernel.learn(os.path.join(aiml_dir, file_name))
        kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
        kernel.saveBrain(brain)
    # print("Learned patterns: ")
    # kernel._brain.dump()
    kernel.setPredicate("name", unknown.lower())
    kernel.setPredicate("age", unknown.lower())
    kernel.setPredicate("job", unknown.lower())

    for bot in to_be_imported:  # import everything that is to be imported
        for file_name in to_be_imported.get(bot, []):
            import_bot_data(file_name, bot)


def init_users():
    global users
    if not os.path.exists(users_file):
        with open(users_file, "w") as f:
            json.dump(dict(), f)
    else:
        with open(users_file) as f:
            try:
                data = json.loads(f.read())
                users = data
            except Exception:
                print("Failed to import users data..")


def get_new_session_id(upper_limit=100000):
    sessions_list = sessions.values()
    rand_session = random.randint(1, upper_limit)
    while rand_session in sessions_list:
        rand_session = random.randint(1, upper_limit)
    return rand_session


def aiml_response(text):
    global current_session_id, last_chat_time
    last_chat_time = time.time()
    return kernel.respond(text, sessions[current_session_id]) \
        if current_session_id else kernel.respond(text)


def get(predicate):
    return kernel.getPredicate(predicate)
    # if not current_session_id else \
    # kernel.getPredicate(predicate, sessionID=current_session_id)


def get_user(predicate):
    if current_user not in users:
        res = get(predicate)
        if not res:
            res = ""
        return res
    else:
        return users[current_user].get(predicate, "")


def update_session():
    global caller, caller_fmt, current_user, users
    name = get("name")
    if not name:
        return
    caller = caller_fmt.format(name)
    if name not in users:
        users[name] = dict()
        kernel.setPredicate("job", unknown.lower())
        kernel.setPredicate("age", unknown.lower())
    elif name != current_user:
        current_user = name
        kernel.setPredicate("name", current_user)
        kernel.setPredicate("job", users[current_user].get("job", unknown.lower()))
        kernel.setPredicate("age", users[current_user].get("age", unknown.lower()))
        return
    job = get("job")
    if job and job != users[name].get("job", ""):
        users[name]["job"] = job
    age = get("age")
    print("Age: ", age)
    if age and age != users[name].get("age", ""):
        users[name]["age"] = age
    print(users)


def process_response(answer):
    """
    Processes response and prints to screen the result
    :param answer: aiml response
    """
    # print(answer)
    # print("answer: {} |{}|".format(len(answer), answer))

    text_split = answer.split('|')
    for index in range(len(text_split)):
        # executes everything between `exec(` and `)`
        if text_split[index].startswith('exec('):
            text_split[index] = eval(text_split[index][5:-1])

    answer = "".join(text_split)
    print(bot_str + answer)


def get_age_limits():
    if current_user not in users or not users[current_user].get("age", None):
        return None
    age = users[current_user].get("age", None)
    if not isinstance(age, int):
        try:
            age = int(age)
        except Exception:
            return None

    for index in range(len(limits[0])):
        if limits[0][index] <= age <= limits[1][index]:
            return [limits[0], limits[1]]
    return None


def process_age(lower_limit, upper_limit):
    return aiml_response(age_fmt.format(lower_limit, upper_limit))


def ask_questions():
    global last_chat_time
    while True:
        if last_chat_time == 0:
            break
        sleep_time = last_chat_time + delay - time.time()
        if sleep_time <= 0:
            sleep_time = 1
        time.sleep(sleep_time)
        if last_chat_time - time.time() >= delay:
            age_limits = get_age_limits()
            print(process_age(age_limits[0], age_limits[1]))


def update_daemons(kill=False):
    global daemons, last_chat_time
    if not kill:
        th = threading.Thread(target=ask_questions)
        th.start()
        daemons.append(th)
    else:
        last_chat_time = 0
        for th in daemons:
            daemons.remove(th)
            th._stop_event.stop()


if __name__ == '__main__':
    if os.path.exists(brain):
        os.remove(brain)
    init_brain()
    init_users()

    update_daemons()
    while True:
        message = get_text(caller)
        if message == 'exit':
            break
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

    with open(users_file, "w") as out:
        json.dump(users, out)
    update_daemons(True)
