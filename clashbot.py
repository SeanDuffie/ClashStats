
""" @file events.py
    @author
    @brief Clan Event Handler
"""
import asyncio
import datetime
import logging
import os
import sys
from typing import List

import coc
import discord
import discord.ext
import discord.ext.commands
import discord.ext.tasks
import pandas as pd
from coc import utils
from dotenv import load_dotenv, set_key

import log_format
from database import Database

### PATH SECTION ###
RTDIR = os.path.dirname(__file__)
DBDIR = os.path.join(RTDIR, "data")
LOGDIR = os.path.join(RTDIR, "logs")
ENVDIR = os.path.join(RTDIR, ".env")

### DATABASE SECTION ###
DB = Database("stats.db", DBDIR)
DB.create_table(
    t_name="roster",
    cols=[
        ("COC", "text", ""),
        ("Discord", "text", "")
    ]
)
DB.create_table(
    t_name="trophies",
    cols=[
        ("Date", "text", ""),
        ("Clan", "text", ""),
        ("PlayerTag", "text", ""),
        ("PlayerName", "text", ""),
        ("Trophies", "int", "")
    ]
)
DB.create_table(
    t_name="donations",
    cols=[
        ("Date", "text", ""),
        ("Clan", "text", ""),
        ("DonorTag", "text", ""),
        ("DonorName", "text", ""),
        ("RecipientTag", "text", ""),
        ("RecipientName", "text", ""),
        ("Amount", "int", "")
    ]
)
DB.close()

### LOGGING SECTION ###
logname = os.path.join(LOGDIR, f'clashbot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
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

CHANNELS = {
    "DEFAULT": 0,
    "WARS": 0,
    "RAID": 0,
    "GAME": 0,
    "RANK": 0,
    "DONATIONS": 0,
    "WELCOME": 0
}

bot = discord.ext.commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    """_summary_
    """
    await find_channels()
    msg = "Clash Stats has been started!"
    logger.info(msg)
    try:
        if CHANNELS["DEFAULT"]:
            await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
        else:
            logger.error("No Default Channel set!")
    except AttributeError:
        logger.error("No channel found with ID: %d", CHANNELS["DEFAULT"])

### Clan Events ###
@coc.ClanEvents.member_donations()
async def on_clan_member_donation(old_member: coc.ClanMember, new_member: coc.ClanMember):
    """ Event triggers every time the troops are donated

    TODO: Update the Troops DONATED on a daily basis?

    Args:
        old_member (coc.ClanMember): _description_
        new_member (coc.ClanMember): _description_
    """
    DB.create_connection("stats.db", DBDIR)
    final_donated_troops = new_member.donations - old_member.donations
    new_donations = pd.DataFrame([[
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            new_member.clan.tag,
            new_member.tag,
            new_member.name,
            "DonatedTag",
            "DonatedName",
            final_donated_troops
    ]])
    for row in new_donations.itertuples(index=False, name=None):
        DB.insert_row("donations", row=row)
        break
    DB.close()

    msg = "{} of {} just donated {} troops.".format(
            new_member,
            new_member.clan,
            final_donated_troops
    )
    logger.info(msg)
    # if CHANNELS["DONATIONS"]:
    #     await bot.get_channel(CHANNELS["DONATIONS"]).send(msg)
    # elif CHANNELS["DEFAULT"]:
    #     logger.warning("No Donation Channel set!")
    #     await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    # else:
    #     logger.warning("No Donation Channel set!")
    #     logger.error("No Default Channel set!")


@coc.ClanEvents.member_received()
async def on_clan_member_donation_receive(old_member: coc.ClanMember, new_member: coc.ClanMember):
    """ Event triggers every time a member receives a donation

    TODO: Update the Troops RECEIVED count on a daily basis?

    Args:
        old_member (coc.ClanMember): _description_
        new_member (coc.ClanMember): _description_
    """
    DB.create_connection("stats.db", DBDIR)
    final_received_troops = new_member.received - old_member.received
    new_donations = pd.DataFrame([[
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            new_member.clan.tag,
            "ReceivedTag",
            "ReceivedName",
            new_member.tag,
            new_member.name,
            final_received_troops
    ]])
    for row in new_donations.itertuples(index=False, name=None):
        DB.insert_row("donations", row=row)
        break
    DB.close()

    msg = "{} of {} just received {} troops.".format(
        new_member,
        new_member.clan,
        final_received_troops
    )
    logger.info(msg)
    # if CHANNELS["DONATIONS"]:
    #     await bot.get_channel(CHANNELS["DONATIONS"]).send(msg)
    # elif CHANNELS["DEFAULT"]:
    #     logger.warning("No Donation Channel set!")
    #     await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    # else:
    #     logger.warning("No Donation Channel set!")
    #     logger.error("No Default Channel set!")


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
    if CHANNELS["WELCOME"]:
        await bot.get_channel(CHANNELS["WELCOME"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No Welcome Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No Welcome Channel set!")
        logger.error("No Default Channel set!")


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
    if CHANNELS["WELCOME"]:
        await bot.get_channel(CHANNELS["WELCOME"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No Welcome Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No Welcome Channel set!")
        logger.error("No Default Channel set!")


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
    # if CHANNELS["RANK"]:
    #     await bot.get_channel(CHANNELS["RANK"]).send(msg)
    # elif CHANNELS["DEFAULT"]:
    #     logger.warning("No Rank Channel set!")
    #     await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    # else:
    #     logger.warning("No Rank Channel set!")
    #     logger.error("No Default Channel set!")

@coc.ClanEvents.member_trophies()
async def clan_member_trophies_changed(old_member: coc.ClanMember, new_member: coc.ClanMember):
    """ Event triggered when number of regular trophies change for a player.

    Args:
        old_member (coc.ClanMember): _description_
        new_member (coc.ClanMember): _description_
    """
    DB.create_connection("stats.db", DBDIR)
    new_trophies = pd.DataFrame([[
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        new_member.clan.tag,
        new_member.tag,
        new_member.trophies
    ]])
    for row in new_trophies.itertuples(index=False, name=None):
        DB.insert_row("trophies", row=row)
        break
    DB.close()

    msg = "{} trophies changed from {} to {}".format(
        new_member,
        old_member.trophies,
        new_member.trophies
    )
    logger.info(msg)
    # if CHANNELS["RANK"]:
    #     await bot.get_channel(CHANNELS["RANK"]).send(msg)
    # elif CHANNELS["DEFAULT"]:
    #     logger.warning("No Rank Channel set!")
    #     await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    # else:
    #     logger.warning("No Rank Channel set!")
    #     logger.error("No Default Channel set!")

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
    # if CHANNELS["RANK"]:
    #     await bot.get_channel(CHANNELS["RANK"]).send(msg)
    # elif CHANNELS["DEFAULT"]:
    #     logger.warning("No Rank Channel set!")
    #     await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    # else:
    #     logger.warning("No Rank Channel set!")
    #     logger.error("No Default Channel set!")


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
    if CHANNELS["WARS"]:
        await bot.get_channel(CHANNELS["WARS"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No War Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No War Channel set!")
        logger.error("No Default Channel set!")


@coc.WarEvents.new_war()
async def new_war(war: coc.ClanWar):
    """ Event Launched when a new war is started

    Args:
        war (coc.ClanWar): _description_
    """
    msg = f"New war against {war.opponent.name} detected."
    logger.info(msg)
    if CHANNELS["WARS"]:
        await bot.get_channel(CHANNELS["WARS"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No War Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No War Channel set!")
        logger.error("No Default Channel set!")


### Client Events ###
@coc.ClientEvents.maintenance_start()
async def on_maintenance():
    """_summary_
    """
    logger.warning("Maintenace Started")


@coc.ClientEvents.maintenance_completion()
async def on_maintenance_completion(time_started: datetime.datetime):
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
    if CHANNELS["DEFAULT"]:
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.error("No Default Channel set!")


@coc.ClientEvents.clan_games_start()
async def clan_games_started():
    """ Event triggered when the clan games start """
    msg = "Clan games have started! Finish your challenges before {}!".format(
        utils.get_clan_games_end()
    )
    logger.info(msg)
    if CHANNELS["GAME"]:
        await bot.get_channel(CHANNELS["GAME"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No Clan Game Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No Clan Game Channel set!")
        logger.error("No Default Channel set!")

@coc.ClientEvents.clan_games_end()
async def clan_games_ended():
    """ Event triggered when the clan games end
    TODO: Record Score???
    """
    msg = "Clan games have ended. The next ones will start at {}".format(
        utils.get_clan_games_start()
    )
    logger.info(msg)
    if CHANNELS["GAME"]:
        await bot.get_channel(CHANNELS["GAME"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No Clan Game Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No Clan Game Channel set!")
        logger.error("No Default Channel set!")


@coc.ClientEvents.raid_weekend_start()
async def raid_weekend_started():
    """ Event triggered when the raid weekend starts """
    msg = "A new Raid Weekend started! Finish your attacks before {}!".format(
        utils.get_raid_weekend_end()
    )
    logger.info(msg)
    if CHANNELS["RAID"]:
        await bot.get_channel(CHANNELS["RAID"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No Raid Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No Raid Channel set!")
        logger.error("No Default Channel set!")

@coc.ClientEvents.raid_weekend_end()
async def raid_weekend_ended():
    """ Event triggered when the raid weekend ends

    TODO: Record stats from the raid
    """
    msg = "The Raid Weekend has ended. Next one will start at {}".format(
        utils.get_raid_weekend_start()
    )
    logger.info(msg)
    if CHANNELS["RAID"]:
        await bot.get_channel(CHANNELS["RAID"]).send(msg)
    elif CHANNELS["DEFAULT"]:
        logger.warning("No Raid Channel set!")
        await bot.get_channel(CHANNELS["DEFAULT"]).send(msg)
    else:
        logger.warning("No Raid Channel set!")
        logger.error("No Default Channel set!")


async def find_channels() -> None:
    channels = bot.get_all_channels()
    global CHANNELS
    for channel in channels:
        if isinstance(channel, discord.TextChannel):
            if "general" in channel.name.lower():
                CHANNELS["DEFAULT"] = channel.id
                logger.info("General Channel changed to: %d (#%s)", CHANNELS["DEFAULT"], channel.name)

            if "donations" in channel.name.lower():
                CHANNELS["DONATIONS"] = channel.id
                logger.info("Donation Channel changed to: %d (#%s)", CHANNELS["DONATIONS"], channel.name)

            if "game" in channel.name.lower():
                CHANNELS["GAME"] = channel.id
                logger.info("Clan Games Channel changed to: %d (#%s)", CHANNELS["GAME"], channel.name)

            if "raid" in channel.name.lower():
                CHANNELS["RAID"] = channel.id
                logger.info("Raid Channel changed to: %d (#%s)", CHANNELS["RAID"], channel.name)

            if "rank" in channel.name.lower():
                CHANNELS["RANK"] = channel.id
                logger.info("Rank Channel changed to: %d (#%s)", CHANNELS["RANK"], channel.name)

            if "war" in channel.name.lower():
                CHANNELS["WARS"] = channel.id
                logger.info("War Channel changed to: %d (#%s)", CHANNELS["WARS"], channel.name)

            if "welcome" in channel.name.lower():
                CHANNELS["WELCOME"] = channel.id
                logger.info("Welcome Channel changed to: %d (#%s)", CHANNELS["WELCOME"], channel.name)

async def main(clan_tags: List[str]) -> None:
    """ Launches the clan event handler as a separate async task.

    Args:
        clan_tags (List[str]): List of clan tags that are being monitored
    """
    async with coc.EventsClient() as coc_client:
        # Attempt to log into CoC API using your credentials. You must use the
        # coc.EventsClient to enable event listening
        try:
            await coc_client.login(
                DEV_EMAIL,
                DEV_PASSWORD
            )
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
        bot.coc_client = coc_client
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    # Unlike the other examples that use `asyncio.run()`, in order to run
    # events forever you must set the event loop to run forever so we will use
    # the lower level function calls to handle this.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Using the loop context, run the main function then set the loop
        # to run forever so that it continuously monitors for events
        CT = [CLAN_TAG]
        loop.run_until_complete(main(clan_tags=CT))
    except KeyboardInterrupt:
        pass
