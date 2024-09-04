
""" @file events.py
    @author
    @brief Clan Event Handler
"""
import asyncio
import logging
import os
import sys
from typing import List

import coc
from coc import utils
from dotenv import load_dotenv, set_key
import discord
import discord.ext
import discord.ext.commands
import discord.ext.tasks

import log_format

### PATH SECTION ###
RTDIR = os.path.dirname(__file__)
ENVDIR = f"{RTDIR}/../.env"

### LOGGING SECTION ###
logname = os.path.join(RTDIR, 'clan_events.log')
log_format.format_logs(logger_name="Clash", file_name=logname, level=logging.DEBUG)
logger = logging.getLogger("Clash")

############ GET ENVIRONMENT VARIABLES ############
load_dotenv(dotenv_path=ENVDIR)
DEV_EMAIL = os.getenv("DEV_EMAIL")
if DEV_EMAIL is None:
    DEV_EMAIL = input("Enter the developer account email: ")
    set_key(
        dotenv_path=ENVDIR,
        key_to_set="DEV_EMAIL",
        value_to_set=DEV_EMAIL
    )
DEV_PASSWORD = os.getenv("DEV_PASSWORD")
if DEV_PASSWORD is None:
    DEV_PASSWORD = input("Enter the developer account password: ")
    set_key(
        dotenv_path=ENVDIR,
        key_to_set="DEV_PASSWORD",
        value_to_set=DEV_PASSWORD
    )
CLAN_TAG = os.getenv("CLAN_TAG")
if CLAN_TAG is None:
    CLAN_TAG = input("Enter the clan tag: ")
    set_key(
        dotenv_path=ENVDIR,
        key_to_set="CLAN_TAG",
        value_to_set=CLAN_TAG
    )
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    DISCORD_TOKEN = input("Enter the discord bot token: ")
    set_key(
        dotenv_path=ENVDIR,
        key_to_set="DISCORD_TOKEN",
        value_to_set=DISCORD_TOKEN
    )
###################################################

CHANNEL_DEFAULT = 0
CHANNEL_WARS = 0
CHANNEL_RAID = 0
CHANNEL_GAME = 0
CHANNEL_RANK = 0
CHANNEL_DONATIONS = 0
CHANNEL_WELCOME = 0

bot = discord.ext.commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    """_summary_
    """
    msg = "Clash Stats has been started!"
    logger.info(msg)
    try:
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)
    except AttributeError:
        logger.error("No channel found with ID: %d", CHANNEL_DEFAULT)

### Clan Events ###
@coc.ClanEvents.member_donations()
async def on_clan_member_donation(old_member: coc.ClanMember, new_member: coc.ClanMember):
    """ Event triggers every time the troops are donated

    TODO: Update the Troops DONATED on a daily basis?

    Args:
        old_member (coc.ClanMember): _description_
        new_member (coc.ClanMember): _description_
    """
    final_donated_troops = new_member.donations - old_member.donations
    msg = "{} of {} just donated {} troops.".format(
            new_member,
            new_member.clan,
            final_donated_troops
    )
    logger.info(msg)
    if CHANNEL_DONATIONS:
        await bot.get_channel(CHANNEL_DONATIONS).send(msg)
    else:
        logger.warning("No Donation Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)
    print(type(old_member), type(new_member))


@coc.ClanEvents.member_received()
async def on_clan_member_donation_receive(old_member: coc.ClanMember, new_member: coc.ClanMember):
    """ Event triggers every time a member receives a donation

    TODO: Update the Troops RECEIVED count on a daily basis?

    Args:
        old_member (coc.ClanMember): _description_
        new_member (coc.ClanMember): _description_
    """
    final_received_troops = new_member.received - old_member.received
    msg = "{} of {} just received {} troops.".format(
        new_member,
        new_member.clan,
        final_received_troops
    )
    logger.info(msg)
    if CHANNEL_DONATIONS:
        await bot.get_channel(CHANNEL_DONATIONS).send(msg)
    else:
        logger.warning("No Donation Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)
    print(type(old_member), type(new_member))


@coc.ClanEvents.member_join()
async def on_clan_member_join(member: coc.ClanMember, clan: coc.Clan):
    """ Event Triggers when a member joins

    TODO: Add to Roster (Roster Score 1)

    Args:
        member (coc.ClanMember): Member that joined
        clan (coc.Clan): Clan object
    """
    msg = "{} has joined {}".format(
        member.name,
        clan.name
    )
    logger.info(msg)
    if CHANNEL_WELCOME:
        await bot.get_channel(CHANNEL_WELCOME).send(msg)
    else:
        logger.warning("No Welcome Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)
    print(type(member), type(clan))
    ranks = {
        -1: "left",
        0: "gone",
        1: "joined",
        2: "member",
        3: "elder",
        4: "coleader",
        5: "leader"
    }


@coc.ClanEvents.member_leave()
async def on_clan_member_leave(member: coc.ClanMember, clan: coc.Clan):
    """ Event Triggers when a member leaves

    TODO: Set Roster Score to -1 for a day

    Args:
        member (coc.ClanMember): Member that left
        clan (coc.Clan): Clan object
    """
    msg = "{} has left {}".format(
        member.name,
        clan.name
    )
    logger.info(msg)
    if CHANNEL_WELCOME:
        await bot.get_channel(CHANNEL_WELCOME).send(msg)
    else:
        logger.warning("No Welcome Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)
    print(type(member), type(clan))


@coc.ClanEvents.points()
async def on_clan_trophy_change(old_clan: coc.Clan, new_clan: coc.Clan):
    """ Event occurs when the whole clan has a trophy change

    TODO: Record daily values

    Args:
        old_clan (coc.Clan): Clan object from before change
        new_clan (coc.Clan): Clan object from after change
    """
    msg = "{} total trophies changed from {} to {}".format(
        new_clan.name,
        old_clan.points,
        new_clan.points
    )
    logger.info(msg)
    if CHANNEL_RANK:
        await bot.get_channel(CHANNEL_RANK).send(msg)
    else:
        logger.warning("No Rank Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)

@coc.ClanEvents.member_trophies()
async def clan_member_trophies_changed(old_member: coc.ClanMember, new_member: coc.ClanMember):
    """ Event triggered when number of regular trophies change for a player.

    Args:
        old_member (coc.ClanMember): _description_
        new_member (coc.ClanMember): _description_
    """
    msg = "{} trophies changed from {} to {}".format(
        new_member,
        old_member.trophies,
        new_member.trophies
    )
    logger.info(msg)
    if CHANNEL_RANK:
        await bot.get_channel(CHANNEL_RANK).send(msg)
    else:
        logger.warning("No Rank Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)

@coc.ClanEvents.member_builder_base_trophies()
async def clan_member_builder_base_trophies_changed(old_member: coc.ClanMember, new_member: coc.ClanMember):
    """ Event triggered when builder base trophies change

    Args:
        old_member (coc.ClanMember): _description_
        new_member (coc.ClanMember): _description_
    """
    msg = "{} builder_base trophies changed from {} to {}".format(
        new_member,
        old_member.builder_base_trophies,
        new_member.builder_base_trophies
    )
    logger.info(msg)
    if CHANNEL_RANK:
        await bot.get_channel(CHANNEL_RANK).send(msg)
    else:
        logger.warning("No Rank Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)


### War Events ###
@coc.WarEvents.war_attack()
async def current_war_stats(attack: coc.WarAttack, war: coc.ClanWar):
    """_summary_

    Args:
        attack (coc.WarAttack): _description_
        war (coc.ClanWar): _description_
    """
    logger.warning(
        "Current War Ends: %s",
        war.end_time
    )

    msg = "\tAttack number {}\n({}).{} of {} attacked ({}).{} of {}".format(
        attack.order,
        attack.attacker.map_position,
        attack.attacker,
        attack.attacker.clan,
        attack.defender.map_position,
        attack.defender,
        attack.defender.clan
    )
    logger.info(msg)
    if CHANNEL_WARS:
        await bot.get_channel(CHANNEL_WARS).send(msg)
    else:
        logger.warning("No War Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)


@coc.WarEvents.new_war()
async def new_war(war: coc.ClanWar):
    """ Event Launched when a new war is started

    Args:
        war (coc.ClanWar): _description_
    """
    msg = f"New war against {war.opponent.name} detected."
    logger.info(msg)
    if CHANNEL_WARS:
        await bot.get_channel(CHANNEL_WARS).send(msg)
    else:
        logger.warning("No War Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)


### Client Events ###
@coc.ClientEvents.maintenance_start()
async def on_maintenance():
    """_summary_
    """
    logger.warning("Maintenace Started")


@coc.ClientEvents.maintenance_completion()
async def on_maintenance_completion(time_started):
    """_summary_

    Args:
        time_started (_type_): _description_
    """
    logger.warning("Maintenace Ended; started at %s", time_started)


@coc.ClientEvents.new_season_start()
async def season_started():
    """_summary_
    """
    msg = "New season started, and will finish at {}".format(
        utils.get_season_end()
    )
    logger.info(msg)
    if CHANNEL_DEFAULT:
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)
    else:
        logger.warning("No General Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)


@coc.ClientEvents.clan_games_start()
async def clan_games_started():
    """ Event triggered when the clan games start """
    msg = "Clan games have started! Finish your challenges before {}!".format(
        utils.get_clan_games_end()
    )
    logger.info(msg)
    if CHANNEL_GAME:
        await bot.get_channel(CHANNEL_GAME).send(msg)
    else:
        logger.warning("No Game Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)

@coc.ClientEvents.clan_games_end()
async def clan_games_ended():
    """ Event triggered when the clan games end
    TODO: Record Score???
    """
    msg = "Clan games have ended. The next ones will start at {}".format(
        utils.get_clan_games_start()
    )
    logger.info(msg)
    if CHANNEL_GAME:
        await bot.get_channel(CHANNEL_GAME).send(msg)
    else:
        logger.warning("No Game Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)


@coc.ClientEvents.raid_weekend_start()
async def raid_weekend_started():
    """ Event triggered when the raid weekend starts """
    msg = "A new Raid Weekend started! Finish your attacks before {}!".format(
        utils.get_raid_weekend_end()
    )
    logger.info(msg)
    if CHANNEL_RAID:
        await bot.get_channel(CHANNEL_RAID).send(msg)
    else:
        logger.warning("No Raid Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)

@coc.ClientEvents.raid_weekend_end()
async def raid_weekend_ended():
    """ Event triggered when the raid weekend ends

    TODO: Record stats from the raid
    """
    msg = "The Raid Weekend has ended. Next one will start at {}".format(
        utils.get_raid_weekend_start()
    )
    logger.info(msg)
    if CHANNEL_RAID:
        await bot.get_channel(CHANNEL_RAID).send(msg)
    else:
        logger.warning("No Raid Channel set!")
        await bot.get_channel(CHANNEL_DEFAULT).send(msg)


async def find_channels() -> None:
    channels = bot.get_all_channels()
    for channel in channels:
        if "general" in channel.name.lower():
            global CHANNEL_DEFAULT
            CHANNEL_DEFAULT = channel.id
        if "donations" in channel.name.lower():
            global CHANNEL_DONATIONS
            CHANNEL_DONATIONS = channel.id
        if "game" in channel.name.lower():
            global CHANNEL_GAME
            CHANNEL_GAME = channel.id
        if "raid" in channel.name.lower():
            global CHANNEL_RAID
            CHANNEL_RAID = channel.id
        if "rank" in channel.name.lower():
            global CHANNEL_RANK
            CHANNEL_RANK = channel.id
        if "war" in channel.name.lower():
            global CHANNEL_WARS
            CHANNEL_WARS = channel.id
        if "welcome" in channel.name.lower():
            global CHANNEL_WELCOME
            CHANNEL_WELCOME = channel.id

async def main(clan_tags: List[str]) -> None:
    """ Launches the clan event handler as a separate async task.

    Args:
        clan_tags (List[str]): List of clan tags that are being monitored
    """
    coc_client = coc.EventsClient()

    # Attempt to log into CoC API using your credentials. You must use the
    # coc.EventsClient to enable event listening
    try:
        await coc_client.login(DEV_EMAIL,
                               DEV_PASSWORD)
    except coc.InvalidCredentials as error:
        sys.exit(error)

    # Register all the clans you want to track
    coc_client.add_clan_updates(*clan_tags)

    # Register all the players you want to track
    async for clan in coc_client.get_clans(clan_tags):
        coc_client.add_player_updates(*[member.tag for member in clan.members])

    # Register all the callback functions that are triggered when a
    # event if fired.
    coc_client.add_events(
        on_clan_member_donation,
        on_clan_member_donation_receive,
        on_clan_member_join,
        on_clan_member_leave,
        on_clan_trophy_change,
        clan_member_trophies_changed,
        clan_member_builder_base_trophies_changed,
        current_war_stats,
        new_war,
        on_maintenance,
        on_maintenance_completion,
        season_started,
        clan_games_started,
        clan_games_ended,
        raid_weekend_started,
        raid_weekend_ended
    )


if __name__ == "__main__":
    # Unlike the other examples that use `asyncio.run()`, in order to run
    # events forever you must set the event loop to run forever so we will use
    # the lower level function calls to handle this.
    loop = asyncio.get_event_loop()
    find_channels()
    bot.run(DISCORD_TOKEN)

    try:
        # Using the loop context, run the main function then set the loop
        # to run forever so that it continuously monitors for events
        CT = [CLAN_TAG]
        loop.run_until_complete(main(clan_tags=CT))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
