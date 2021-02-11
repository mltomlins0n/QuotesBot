import discord
import os
import requests
import json
import random
from replit import db

# Create an instance of a client to connect to discord
client = discord.Client()

# List of words that will trigger encouragemenent
sad_words = ["sad", "depressed", "depressing", "miserable", "unhappy",
"upsetting", "upset"]

# Encouraging messages
starter_encouragements = [
  "You've got this",
  "Never give up!",
  "Hang in there, it'll get better",
  "Sleep on it, I'm sure you'll change your mood",
  "Maybe this will help: https://www.youtube.com/watch?v=KxGRhd_iWuE"
]

# Boolean to decide if the bot is responding to trigger words
if 'responding' not in db.keys():
  db['responding'] = True

# Returns a quote from the API
def get_quote():
  response = requests.get('https://zenquotes.io/api/random')
  json_data = json.loads(response.text)
  # Get the quote and author from the API response
  quote = json_data[0] ['q'] + ' - ' + json_data[0] ['a']
  return quote

# TODO - Get random jokes from an API

# Allow users to add custom encouraging messages
def update_encouragement(encouraging_message):
  # Get all messages, add the new one and resave the database
  if 'encouragements' in db.keys():
    encouragements = db['encouragements']
    encouragements.append(encouraging_message)
    db['encouragements'] = encouragements
  else: # Create a new entry in the database
    db['encouragements'] = [encouraging_message]

# Delete a message
def delete_encouragement(index):
  encouragements = db['encouragements']
  if len(encouragements) > index:
    del encouragements[index]
    db['encouragements'] = encouragements

# Register an event
@client.event
# When bot is ready
async def on_ready():
  print('Logged in as {0.user}'.format(client))

@client.event
# If bot receives a message
async def on_message(message):
  if message.author == client.user:
    return

  # The content of a user's message
  msg = message.content

  # The command to trigger the bot
  if msg.startswith('!inspire'):
    quote = get_quote()
    # The bot's reply
    await message.channel.send(quote)

  if db['responding']:
    options = starter_encouragements
    if 'encouragements' in db.keys():
      options = options + db['encouragements']

    # Check for any trigger words and send a random encouraging response
    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))
      # Send a PM to the user
      #await message.author.send(random.choice(starter_encouragements))

  # Add new message to database from a Discord command
  if msg.startswith('!new'):
    # Get the text after the !new command
    encouraging_message = msg.split('!new ',1)[1]
    update_encouragement(encouraging_message)
    await message.channel.send('New encouraging message added, nice!')
  
  # Delete a message
  if msg.startswith('!del'):
    encouragements = []
    if 'encouragements' in db.keys():
      # Get the index of the message to be deleted
      index = int(msg.split('!del',1)[1])
      delete_encouragement(index)
      encouragements = db['encouragements']
    await message.channel.send('Current custom responses are: \n')
    await message.channel.send(encouragements) # send updated list

  # List messages
  if msg.startswith('!list'):
    encouragements = []
    if 'encouragements' in db.keys():
      encouragements = db['encouragements']
    await message.channel.send('Current custom responses are: \n')
    await message.channel.send(encouragements)

  # Set whether the bot responds to trigger words
  if msg.startswith('!responding'):
    value = msg.split('!responding ',1)[1]
    if value.lower() == 'on':
      db['responding'] = True
      await message.channel.send('Responding is on.')
    else:
      db['responding'] = False
      await message.channel.send('Responding is off. IDGAF about your sadness.')

# Run the bot
client.run(os.getenv('TOKEN'))