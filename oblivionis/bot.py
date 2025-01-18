import datetime
import logging
import os

import discord
from discord.ext import commands

from oblivionis import storage

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.presences = True
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


@bot.event
async def on_guild_available(guild):
    logger.info("Server %s available", guild)


@bot.event
async def on_presence_update(before, after):
    logger.debug("User presence changed")
    if after.activity == before.activity:
        return

    if after.activity is None and before.activity.type == discord.ActivityType.playing:
        activity = before.activity
        duration = datetime.datetime.now(datetime.UTC) - activity.start
        duration_seconds = round(duration.total_seconds())
        logger.info(
            "Member %s has stopped playing %s after %s seconds",
            after,
            activity.name,
            duration_seconds,
        )
        user, user_created = storage.User.get_or_create(
            id=before.id, defaults={"name": before.name}
        )
        if user_created:
            logger.info("Added new user '%s' to database", before.name)
        game, game_created = storage.Game.get_or_create(name=activity.name)
        if game_created:
            logger.info("Added new game '%s' to database", game.name)
        storage.Activity.create(user=user, game=game, seconds=duration_seconds)
    elif after.activity.type == discord.ActivityType.playing:
        logger.info("Member %s has started playing %s", after, after.activity.name)


@bot.event
async def on_ready():
    logger.info("Oblivionis is ready")


def main():
    storage.connect_db()
    bot.run(os.environ["TOKEN"])


if __name__ == "__main__":
    main()
