
""" @file events.py
    @author
    @brief Clan Event Handler
"""
import asyncio
import logging
import os

import coc
from coc import utils
from dotenv import load_dotenv, set_key

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

### Clan Events ###
@coc.ClanEvents.member_donations()
async def on_clan_member_donation(old_member, new_member):
    """_summary_

    Args:
        old_member (_type_): _description_
        new_member (_type_): _description_
    """
    final_donated_troops = new_member.donations - old_member.donations
    logger.info(
        "%s of %s just donated %s troops.",
        new_member,
        new_member.clan,
        final_donated_troops
    )


@coc.ClanEvents.member_received()
async def on_clan_member_donation_receive(old_member, new_member):
    """_summary_

    Args:
        old_member (_type_): _description_
        new_member (_type_): _description_
    """
    final_received_troops = new_member.received - old_member.received
    logger.info(
        "%s of %s just received %s troops.",
        new_member,
        new_member.clan,
        final_received_troops
    )


@coc.ClanEvents.member_join()
async def on_clan_member_join(member, clan):
    """_summary_

    Args:
        member (_type_): _description_
        clan (_type_): _description_
    """
    logger.info(
        "%s has joined %s",
        member.name,
        clan.name
    )


@coc.ClanEvents.member_leave()
async def on_clan_member_leave(member, clan):
    """_summary_

    Args:
        member (_type_): _description_
        clan (_type_): _description_
    """
    logger.info(
        "%s has left %s",
        member.name,
        clan.name
    )


@coc.ClanEvents.points()
async def on_clan_trophy_change(old_clan, new_clan):
    """_summary_

    Args:
        old_clan (_type_): _description_
        new_clan (_type_): _description_
    """
    logger.info(
        "%s total trophies changed from %s to %s",
        new_clan.name,
        old_clan.points,
        new_clan.points
    )


@coc.ClanEvents.member_builder_base_trophies()
async def clan_member_builder_base_trophies_changed(old_member, new_member):
    """_summary_

    Args:
        old_member (_type_): _description_
        new_member (_type_): _description_
    """
    logger.info(
        "%s builder_base trophies changed from %s to %s",
        new_member,
        old_member.builder_base_trophies,
        new_member.builder_base_trophies
    )


### War Events ###
@coc.WarEvents.war_attack()
async def current_war_stats(attack, war):
    """_summary_

    Args:
        attack (_type_): _description_
        war (_type_): _description_
    """
    logger.info(
        "Attack number %s\n(%s).%s of %s attacked (%s).%s of %s",
        attack.order,
        attack.attacker.map_position,
        attack.attacker,
        attack.attacker.clan,
        attack.defender.map_position,
        attack.defender,
        attack.defender.clan
    )


@coc.WarEvents.new_war()
async def new_war(war):
    """_summary_

    Args:
        war (_type_): _description_
    """
    logger.info("New war against %s detected.", war.opponent.name)


### Player Events ###
@coc.PlayerEvents.donations()
async def on_player_donation(old_player, new_player):
    """_summary_

    Args:
        old_player (_type_): _description_
        new_player (_type_): _description_
    """
    final_donated_troops = new_player.donations - old_player.donations
    logger.info(
        "%s of %s just donated %d troops.",
        new_player,
        new_player.clan,
        final_donated_troops
    )


@coc.PlayerEvents.received()
async def on_player_donation_receive(old_player, new_player):
    """_summary_

    Args:
        old_player (_type_): _description_
        new_player (_type_): _description_
    """
    final_received_troops = new_player.received - old_player.received
    logger.info(
        "%s of %s just received %d troops.",
        new_player,
        new_player.clan,
        final_received_troops
    )


@coc.PlayerEvents.trophies()
async def on_player_trophy_change(old_player, new_player):
    """_summary_

    Args:
        old_player (_type_): _description_
        new_player (_type_): _description_
    """
    logger.info(
        "%s trophies changed from %d to %d",
        new_player,
        old_player.trophies,
        new_player.trophies
    )


@coc.PlayerEvents.builder_base_trophies()
async def on_player_builder_base_trophy_change(old_player, new_player):
    """_summary_

    Args:
        old_player (_type_): _description_
        new_player (_type_): _description_
    """
    logger.info(
        "%s builder_base trophies changed from %d to %d",
        new_player,
        old_player.builder_base_trophies,
        new_player.builder_base_trophies
    )


### Client Events ###
@coc.ClientEvents.maintenance_start()
async def on_maintenance():
    """_summary_
    """
    logger.info("Maintenace Started")


@coc.ClientEvents.maintenance_completion()
async def on_maintenance_completion(time_started):
    """_summary_

    Args:
        time_started (_type_): _description_
    """
    logger.info("Maintenace Ended; started at %s", time_started)


@coc.ClientEvents.new_season_start()
async def season_started():
    """_summary_
    """
    logger.info(
        "New season started, and will finish at %s",
        utils.get_season_end()
    )


@coc.ClientEvents.clan_games_end()
async def clan_games_ended():
    """_summary_
    """
    logger.info(
        "Clan games have ended. The next ones will start at %s",
        utils.get_clan_games_start()
    )


@coc.ClientEvents.raid_weekend_start()
async def raid_weekend_started():
    """_summary_
    """
    logger.info(
        "A new Raid Weekend started. It will last until %s",
        utils.get_raid_weekend_end()
    )


async def main(clan_tags) -> None:
    """_summary_

    Args:
        clan_tags (_type_): _description_
    """
    coc_client = coc.EventsClient()

    # Attempt to log into CoC API using your credentials. You must use the
    # coc.EventsClient to enable event listening
    try:
        await coc_client.login(DEV_EMAIL,
                               DEV_PASSWORD)
    except coc.InvalidCredentials as error:
        exit(error)

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
        clan_member_builder_base_trophies_changed,
        current_war_stats,
        on_player_donation,
        on_player_donation_receive,
        on_player_trophy_change,
        on_player_builder_base_trophy_change,
        on_maintenance,
        on_maintenance_completion,
        season_started
    )


if __name__ == "__main__":
    # Unlike the other examples that use `asyncio.run()`, in order to run
    # events forever you must set the event loop to run forever so we will use
    # the lower level function calls to handle this.
    loop = asyncio.get_event_loop()

    try:
        # Using the loop context, run the main function then set the loop
        # to run forever so that it continuously monitors for events
        CT = [CLAN_TAG]
        loop.run_until_complete(main(clan_tags=CT))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
