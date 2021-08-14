import requests
import pickle
import json

with open("config.json", "r") as file:
    config_data = json.load(file)
API_KEY = config_data["api-key"]
MAX_TOKENS = config_data["max-tokens"]
TEMPERATURE = config_data["temperature"]
TOP_P = config_data["top-p"]


class Agent: # Agent class which pickle can dump to a file
    def __init__(self, name, userName):
        self.name = name
        self.context = ""
        self.conversation = ""
        self.userName = userName

    def save(self):  # Saves the agent object to a file
        file = open(f"{self.name}.mtrx", "wb")
        pickle.dump(self, file)
        file.close()

    def getLog(self, prompt): # Creates a string which is just the context of the agent, plus all of the conversations it has had with the user.
        out = self.context + "\n" + self.conversation + "\n"
        out += f'{self.userName}: {prompt}\n {self.name}: '
        return out

    def getResponse(self, prompt): # Calls the api with all of the required parameters to generate a response
        response = requests.post("https://api.ai21.com/studio/v1/j1-jumbo/complete",
                                 headers={"Authorization": f"Bearer {API_KEY}"},
                                 json={
                                     "prompt": self.getLog(prompt),
                                     "numResults": 1,
                                     "maxTokens": MAX_TOKENS,
                                     "stopSequences": ["\n"],
                                     "temperature": TEMPERATURE,
                                     "topP": TOP_P
                                 })
        responseData = json.loads(response.text)["completions"][0]["data"]["text"]
        return responseData

    def generate(self, prompt, doTraining):
        response = self.getResponse(prompt)
        if doTraining: # Not really training per se, more akin to memory (everything said in the 'training' mode will be remembered by the agent)
            self.conversation += f'{self.userName}: {prompt}\n{agentName}: {response}'
            self.save()
        return response


def loadAgent(name):  # Loads an agent object from a file
    file = open(f"{name}.mtrx", "rb")
    agent = pickle.load(file)
    file.close()
    return agent


def doesFileExist(fileName): # Simply tests if a file exists
    try:
        open(fileName, "r").close()
        exists = True
    except FileNotFoundError:
        exists = False
    return exists


userName = input("Enter your name: ")
agentName = input("Enter the agent's name: ")
doTraining = input("Do you want the agent to remember this conversation? (Y/N): ")
doTraining = False
if doTraining.lower() == "y":
    doTraining = True
if doesFileExist(f"{agentName}.mtrx"):
    agent = loadAgent(agentName)
else:
    context = input("Enter the context: ")
    agent = Agent(agentName, userName)
prompt = None
while True:
    prompt = input(f"{userName}: ")
    if prompt == "":
        break
    print(f'{agentName}: {agent.generate(prompt, doTraining)}')
