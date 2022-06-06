import os
import openai
from dotenv import load_dotenv
import random

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

# from https://read.gov/aesop/001.html
first_lines = [
    "An Ox came down to a reedy pool to drink.",
    "The Mice once called a meeting to decide on a plan to free themselves of their enemy, the Cat.",
    "A Town Mouse once visited a relative who lived in the country.",
    "A Fox one day spied a beautiful bunch of ripe grapes hanging from a vine trained along the branches of a tree. ",
    "A Wolf had been feasting too greedily, and a bone had stuck crosswise in his throat. ",
    "A Lion lay asleep in the forest, his great head resting on his paws.",
    "The Owl always takes her sleep during the day.",
    "Two Travellers, walking in the noonday sun, sought the shade of a widespreading tree to rest.",
    "The Swallow and the Crow had an argument one day about their plumage.",
]


def get_first_line():
    # return a random line from the list
    return first_lines[random.randint(0, len(first_lines) - 1)]


# Generate a line from GPT3
# engine="text-davinci-002"
# engine="text-babbage-001"
def get_next_line(prompt=None, list=None, engine="text-babbage-001"):
    if prompt is None or len(prompt) == 0 and list is not None:
        prompt = "This is Aesop's Fables\n\n"
        # get prompt from the list, last 7 lines
        for line in list[-7:]:
            prompt += line["line"] + "\n###\n"

    results = openai.Completion.create(
        # engine="text-davinci-002",
        engine="text-babbage-001",
        prompt=prompt,
        max_tokens=500,
    )

    return results["choices"][0]["text"]


if __name__ == "__main__":
    first_line = get_first_line()
    print(first_line)
    print(get_next_line(prompt=first_line))
