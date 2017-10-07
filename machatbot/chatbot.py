import os
import aiml

kernel = aiml.Kernel()
aiml_dir = os.path.join(os.path.dirname(__file__), "aiml")
core_dir = os.path.join(os.path.dirname(__file__), "core")
brain = os.path.join(core_dir, "bot_brain.brn")
if not os.path.exists(core_dir) and not os.path.isdir(core_dir):
    os.makedirs(core_dir)

if os.path.isfile(brain):
    kernel.bootstrap(brainFile=brain)
else:
    for file_name in os.listdir(aiml_dir):
        kernel.learn(os.path.join(aiml_dir, file_name))
    kernel.saveBrain(brain)


def aiml_response(message):
    return kernel.respond(message)
