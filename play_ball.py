import pandas as pd
import numpy as np

from utils.inning_utils import *
from utils.mlb_stats import *
from utils.lineup_utils import *


def playball_sim(data_seasons, team_lineup, batter):

    # set up lineup stats
    gm_lineup = Lineup(data_seasons, team_lineup)

    # opponent fielding percentage (%)
    opp_fielding = gm_lineup[9]

    # get the lineup position of the batter
    batter_number = team_lineup.index(batter)

    """
    aPOSlist = [1, 0, 0]  # man on first (no outs)
    aPOSlist = [0, 1, 0]  # man on second (one out: after sac bunt)
    """
    inning_df = pd.DataFrame()
    for i in range(2):
        """
        On the first pass run as if man on 1st, nobody out and swinging away
        On second pass run as if sac bunt runner to 2nd
        """
        if i == 0:
            outs = 0
            baserunners = [1, 0, 0]
        elif i == 1:
            outs = 1
            baserunners = [0, 1, 0]

        if baserunners[0] == 1:
            runner = "1st"
        elif baserunners[1] == 1:
            runner = "2nd"
        elif baserunners[2] == 1:
            runner = "3rd"

        runs = 0
        multi_runs = 0
        for i in range(15000):
            # simulate 15000 innings
            ## total times a run is scored

            inning_rslt = inning(
                bat_lineup=gm_lineup[:9],
                opp_field=opp_fielding,
                batter=batter_number,
                o=outs,
                aPOSlist=baserunners,
            )

            if inning_rslt[0] > 0:
                runs += 1
            if inning_rslt[0] > 1:
                multi_runs += 1

        if inning_df.empty:
            inning_df = pd.DataFrame(
                data={
                    "Play Type": ["Swing Away"],
                    "Inning Setup": [f"Runner on {runner} w/ 0 Out"],
                    "Run %": [runs / 15000],
                    "Multi Run %": [multi_runs / 15000],
                }
            )
        else:
            inning_df = pd.concat(
                [
                    inning_df,
                    pd.DataFrame(
                        data={
                            "Play Type": ["Sac Bunt"],
                            "Inning Setup": [f"Runner on {runner} w/ 1 Out"],
                            "Run %": [runs / 15000],
                            "Multi Run %": [multi_runs / 15000],
                        }
                    ),
                ]
            ).reset_index(drop=True)

    return inning_df


######################################################

# NLDS Game 1
gm_scenario = playball_sim(
    data_seasons=[2024, 2025],
    team_lineup=[
        "Trea Turner",
        "Kyle Schwarber",
        "Bryce Harper",
        "Alec Bohm",
        "JT Realmuto",
        "Nick Castellanos",
        "Bryson Stott",
        "Harrison Bader",
        "Max Kepler",
    ],
    batter="Bryson Stott",
)
