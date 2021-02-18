import discord
import os
import requests
import json
import random
from replit import db
from asyncio import sleep
from keep_alive import keep_alive

# Create an instance of a client to connect to discord
client = discord.Client()
# The default URL of the jokes API to build a request from
baseURL = "https://v2.jokeapi.dev/"

# List of words that will trigger encouragemenent
sad_words = ["sad", "depressed", "depressing", "miserable", "unhappy",
"upsetting", "upset"]

# List of discord emotes for the bot to pick from
emotes = [
  ":bread:",
  ":eyes:",
  ":grimacing:",
  ":joy:",
  ":laughing:",
  ":middle_finger:"
  ":neutral_face:",
  ":ok_hand:",
  ":rofl:",
  ":sweat_smile:",
  ":thinking:",
  ":unamused:",
]

# Encouraging messages
starter_encouragements = [
  "You've got this",
  "Never give up!",
  "Hang in there, it'll get better",
  "Sleep on it, I'm sure you'll change your mood",
  "Maybe this will help: https://www.youtube.com/watch?v=KxGRhd_iWuE"
]

# Boolean to decide if the bot is responding to trigger words
if "responding" not in db.keys():
  db["responding"] = True

# Returns a quote from the API
def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  # Get the quote and author from the API response
  quote = json_data[0] ["q"] + " - " + json_data[0] ["a"]
  return quote

# Get a random joke with no filter
def get_joke():
  response = requests.get(baseURL + "/joke/Any?")
  json_data = json.loads(response.text)
  jokeType = json_data["type"]
  # Check whether the joke is a one liner or not
  if jokeType == "single":
    # Parse the joke from the API response
    joke = json_data["joke"]
    return joke
  else:
    setup = json_data["setup"]
    delivery = json_data["delivery"]
    twoPartJoke = setup + "\n" + delivery
    return twoPartJoke

# Allow users to add custom encouraging messages
def update_encouragement(encouraging_message):
  # Get all messages, add the new one and resave the database
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else: # Create a new entry in the database
    db["encouragements"] = [encouraging_message]

# Delete a message
def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements

# Register an event
@client.event
# When bot is ready
async def on_ready():
  print("Logged in as {0.user}".format(client))
  # Set the bot's presence info
  await client.change_presence(activity = discord.Game("type !commands for help"))

@client.event
# If bot receives a message
async def on_message(message):
  # Stop the bot from replying to itself
  if message.author == client.user:
    return

  # Reply to a mention
  if client.user.mentioned_in(message):
    await message.channel.send("I appreciate the mention, but you don't need to do that. Just type `!commands` for help :sweat_smile:")

  # The content of a user's message
  msg = message.content

  # List the bot's commands
  if msg.startswith("!commands"):
    commands = """>>> Commands: \n
    `!inspire` - Get a random inspiring quote.
    `!joke` - Get a random joke.
    `!list` - List the current custom encouraging messages.
    Use this command before using `!del`, so you know which 
    message you're about to delete.
    Type `!new` followed by your message to add a new
    custom encouraging message, be nice!
    Type `!del` and a no. from 0 to the current no. of custom messages to delete that message in case it turns out to be wildly inappropriate. 
    E.g. `!del 0` deletes the first message in the list.
    `!responding` - use `!responding off` to stop the bot from 
    responding to trigger words.
    use `!responding on` to turn it back on. Responding is on 
    by default.
    """
    await message.channel.send(commands)

  # The command to trigger the bot
  if msg.startswith("!inspire"):
    quote = get_quote()
    # The bot's reply
    await message.channel.send(quote)
  
  # Tell a joke
  if msg.startswith("!joke"):
    joke = get_joke()
    await message.channel.send(joke)
    await sleep(5)
    # Pick a random emote from the emotes list
    await message.channel.send(random.choice(emotes))

  # Check that the bot is responding and that messages exist
  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
      options = options + db["encouragements"]

    # Check for any trigger words and send a random encouraging response
    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))
      # Send a PM to the user
      #await message.author.send(random.choice(starter_encouragements))

  # Add new message to database from a Discord command
  if msg.startswith("!new"):
    # Get the text after the !new command
    encouraging_message = msg.split("!new ",1)[1]
    update_encouragement(encouraging_message)
    await message.channel.send("New encouraging message added, nice!")
  
  # Delete a message
  if msg.startswith("!del"):
    encouragements = []
    if "encouragements" in db.keys():
      # Get the index of the message to be deleted
      index = int(msg.split("!del",1)[1])
      delete_encouragement(index)
      encouragements = db["encouragements"]
    await message.channel.send("Current custom responses are: \n")
    await message.channel.send(encouragements) # send updated list

  # List messages
  if msg.startswith("!list"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send("Current custom responses are: \n")
    await message.channel.send(encouragements)

  # Set whether the bot responds to trigger words
  if msg.startswith("!responding"):
    value = msg.split("!responding ",1)[1]
    if value.lower() == "on":
      db["responding"] = True
      await message.channel.send("Responding is on.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off. IDGAF about your sadness.")

# Run the web server
keep_alive()
# Run the bot
client.run(os.getenv("TOKEN"))