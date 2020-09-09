import discord
import google.cloud.logging
import logging
import os
import sys

from config import API_KEY
from tinydb import TinyDB, Query

db = TinyDB('db.json')

isDev = os.getenv('SPERO_BOT_DEV', False)
if isDev:
  print('Running in dev mode...')

# FIX THIS "LATER" :)
PREFIX = '!!'
REACTION_MSG_COMMAND = PREFIX + 'reaction'

logging.basicConfig(level=logging.INFO)
if not isDev:
  client = google.cloud.logging.Client()
  client.setup_logging(logging.INFO)

logger = logging.getLogger(__name__)

async def set_reaction_msg(message):
  tokens = message.content.split()
  if len(tokens) < 3 or len(message.role_mentions) < 1:
    return
  reaction = tokens[1]
  role = message.role_mentions[0].id
  if not role:
    return
  try:
    await message.add_reaction(reaction)
  except:
    e = sys.exc_info()[0]
    logger.error(e)
    return
  db.insert({'cmd': 'reaction', 'msg_id': message.id, 
             'reaction': reaction, 'role': role})

class BotClient(discord.Client):
  async def on_ready(self):
    logger.info('Logged on as {0}!'.format(self.user))
    await self.change_presence(activity=discord.Game('with your heart, YO!'))

  async def on_message(self, message):
    if (message.author.guild_permissions.administrator 
        and message.content.startswith(PREFIX)):
      if message.content.startswith(REACTION_MSG_COMMAND):
        await set_reaction_msg(message)

  async def on_raw_reaction_add(self, payload):
    if payload.member.bot:
      return
    Command = Query()
    results = db.search(Command.msg_id == payload.message_id 
                        and Command.reaction == str(payload.emoji))
    if payload.member and results:
      role = payload.member.guild.get_role(results[0]['role'])
      if role:
        try:
          await payload.member.add_roles(role)
        except:
          e = sys.exc_info()[0]
          logger.error(e)
          pass

  async def on_raw_reaction_remove(self, payload):
    Command = Query()
    results = db.search(Command.msg_id == payload.message_id 
                        and Command.reaction == str(payload.emoji))
    if not payload.guild_id:
      return
    try:
      guild = self.get_guild(id=payload.guild_id)
      if payload.user_id and guild and results:
        role = guild.get_role(results[0]['role'])
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)
    except:
      e = sys.exc_info()[0]
      logger.error(e)
      pass


client = BotClient()
client.run(API_KEY)