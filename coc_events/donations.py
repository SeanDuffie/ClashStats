
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