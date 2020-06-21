import discord
import google.cloud.logging
import logging
import os

from config import API_KEY

isDev = os.getenv('SPERO_BOT_DEV', False)
print(isDev)

logging.basicConfig(level=logging.INFO)
if not isDev:
  client = google.cloud.logging.Client()
  client.setup_logging(logging.INFO)

logger = logging.getLogger(__name__)

class BotClient(discord.Client):
  
  async def on_ready(self):
    logger.info('Logged on as {0}!'.format(self.user))
    await self.change_presence(activity=discord.Game('with your heart, YO!'))

  async def on_message(self, message):
    # logger.info('Message from {0.author}: {0.content}'.format(message))
    pass

client = BotClient()
client.run(API_KEY)