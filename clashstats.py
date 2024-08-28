""" @file clashstats.py
    @author Sean Duffie
    @brief Tracks weekly clan stats

    Every monday various stats should be collected on members of a clan.

    Monthly:
        - Clan Games (22nd - 28th)
            - Average Score
            - Total Score
        - League Wars (1st - 8th)
            - Score
            - Attacks Used
            - Included
    Weekly:
        - Raids
            - Average Score
            - Total Score
        - Wars
            - Score
            - Attacks Used
            - Included
        - Roster
            - Who is in?
            - What rank are they?
            - Trophy Count
            - TH Level
            - Hero Levels
            
    Features:
        - Pick best war team
        - Pick candidates for promotion
        - Discord
            - General Chatting
                - Main Base
                - Builder Base
                - Raid attacks
                - 
            - Join/Leave Channel
            - War Channel
            - Raid Channel
            - Games Channel
            - Upgrades/Ranking Channel
"""
import logging
import os

import log_format
from clan import Clan
from player import Player

### PATH SECTION ###
RTDIR = os.path.dirname(__file__)

### LOGGING SECTION ###
logname = os.path.join(RTDIR, 'Clash.log')
log_format.format_logs(logger_name="Clash", file_name=logname)
logger = logging.getLogger("Clash")

if __name__ == "__main__":
    clan = Clan("#2LQGUYYQJ")
    plyr = Player("#2QJ9QJ8R")
