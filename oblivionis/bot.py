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

activities = {}


def game_from_activity(activity) -> str:
    if activity.name == "Steam Deck":
        return activity.details.removeprefix("Playing ")
    return activity.name


def get_game_activity(activities):
    """Get the first game activity or None."""
    for activity in activities:
        if activity.type == discord.ActivityType.playing:
            return activity
    return None


def get_stored_activity(member, activity) -> dict | None:
    """Get an applicable activity from the in-memory storage."""
    stored = activities.pop(member.id, None)
    if stored and stored["application_id"] == activity.application_id:
        return stored
    return None


@bot.event
async def on_guild_available(guild):
    logger.info("Server %s available", guild)


@bot.event
async def on_presence_update(before, after):
    logger.debug("User presence changed")
    before_activity = get_game_activity(before.activities)
    after_activity = get_game_activity(after.activities)

    if after_activity == before_activity:
        return

    if before_activity is not None and after_activity is None:
        activity = before_activity

        # Determine how long the activity lasted.
        start = activity.start
        if start is None and (stored_activity := get_stored_activity(after, activity)):
            logger.warning(
                "Discord API did not return activity start time; "
                "falling back to stored value"
            )
            start = stored_activity["start"] or stored_activity["timestamp"]
        if start is None:
            logger.info(
                "Could not determine duration for member %s activity %s",
                after,
                game_from_activity(activity),
            )
            return
        duration = datetime.datetime.now(datetime.UTC) - start
        duration_seconds = round(duration.total_seconds())

        logger.info(
            "Member %s has stopped playing %s after %s seconds",
            after,
            game_from_activity(activity),
            duration_seconds,
        )
        user, user_created = storage.User.get_or_create(
            id=before.id, defaults={"name": before.name}
        )
        if user_created:
            logger.info("Added new user '%s' to database", before.name)

        game, game_created = storage.Game.get_or_create(
            name=game_from_activity(activity)
        )
        if game_created:
            logger.info("Added new game '%s' to database", game.name)
        storage.Activity.create(user=user, game=game, seconds=duration_seconds)
    elif after_activity is not None:
        if (
            after.id not in activities
            or activities[after.id]["application_id"] != after_activity.application_id
        ):
            activities[after.id] = {
                "application_id": after_activity.application_id,
                "name": after_activity.name,
                "start": after_activity.start,
                "timestamp": datetime.datetime.now(datetime.UTC),
            }
        logger.info(
            "Member %s has started playing %s",
            after,
            game_from_activity(after_activity),
        )


@bot.event
async def on_ready():
    logger.info("Oblivionis is ready")


def main():
    storage.connect_db()
    bot.run(os.environ["TOKEN"])


if __name__ == "__main__":
    main()
