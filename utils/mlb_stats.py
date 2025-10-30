import re
import time
import unidecode
import pandas as pd
import requests
from bs4 import BeautifulSoup
from logzero import logger


def player_weighted_avg(season_years, df, metric):
    season_years.sort(reverse=True)
    years = len(season_years)
    player_weight_avg = pd.DataFrame()

    # first year should be weighted the most
    #   3 buckets (2.5, 1.5, 1)
    for player in df.Name.unique().tolist():
        player_df = df[(df["Name"] == f"{player}")]
        player_seasons = player_df.year.tolist()
        player_seasons.sort()

        weight_avg1 = df[
            (df["Name"] == f"{player}") & (df["year"] == player_seasons[0])
        ][f"{metric}"].reset_index(drop=True)[0]
        try:
            weight_avg2 = df[
                (df["Name"] == f"{player}") & (df["year"] == player_seasons[1])
            ][f"{metric}"].reset_index(drop=True)[0]
        except IndexError:
            weight_avg2 = 0
        try:
            weight_avg3 = (
                df[(df["Name"] == f"{player}") & (df["year"].isin(player_seasons[2:]))][
                    f"{metric}"
                ]
                .reset_index(drop=True)
                .mean()
            )
        except IndexError:
            weight_avg3 = 0

        # apply the weights
        if years == 1:
            weight_avg = weight_avg1
        elif years == 2:
            weight_avg = ((weight_avg1 * 3.5) + (weight_avg2 * 1.5)) / 5
        else:
            weight_avg = (
                (weight_avg1 * 2.5) + (weight_avg2 * 1.5) + (weight_avg3 * 1)
            ) / 5

        player_weight_avg = pd.concat(
            [
                player_weight_avg,
                pd.DataFrame(
                    data={
                        "Name": [f"{player}"],
                        f"{metric}": [weight_avg],
                    }
                ),
            ]
        )

    return player_weight_avg


def team_weighted_avg(season_years, df, metric):
    season_years.sort(reverse=True)
    years = len(season_years)
    team_weight_avg = pd.DataFrame()

    # first year should be weighted the most
    #   3 buckets (2.5, 1.5, 1)
    for team in df.Tm.unique().tolist():
        team_df = df[(df["Tm"] == f"{team}")]
        team_seasons = team_df.year.tolist()
        team_seasons.sort()

        weight_avg1 = df[(df["Tm"] == f"{team}") & (df["year"] == team_seasons[0])][
            f"{metric}"
        ].reset_index(drop=True)[0]
        try:
            weight_avg2 = df[(df["Tm"] == f"{team}") & (df["year"] == team_seasons[1])][
                f"{metric}"
            ].reset_index(drop=True)[0]
        except IndexError:
            weight_avg2 = 0
        try:
            weight_avg3 = (
                df[(df["Tm"] == f"{team}") & (df["year"].isin(team_seasons[2:]))][
                    f"{metric}"
                ]
                .reset_index(drop=True)
                .mean()
            )
        except IndexError:
            weight_avg3 = 0

        # apply the weights
        if years == 1:
            weight_avg = weight_avg1
        elif years == 2:
            weight_avg = ((weight_avg1 * 3.5) + (weight_avg2 * 1.5)) / 5
        else:
            weight_avg = (
                (weight_avg1 * 2.5) + (weight_avg2 * 1.5) + (weight_avg3 * 1)
            ) / 5

        team_weight_avg = pd.concat(
            [
                team_weight_avg,
                pd.DataFrame(
                    data={
                        "Tm": [f"{team}"],
                        f"{metric}": [weight_avg],
                    }
                ),
            ]
        )

    return team_weight_avg


def stats(season_years: list):
    full_player_bat_df = pd.DataFrame()
    full_player_pitch_df = pd.DataFrame()
    full_team_field_df = pd.DataFrame()

    for season_year in season_years:
        logger.info(f"Gathering player data for {season_year}")

        # special characters
        special_charc = "*#+"

        # list of team abbreviations
        team_url = f"https://www.baseball-reference.com/about/team_IDs.shtml"
        team_id = pd.read_html(team_url, header=0)[0]
        curr_teams = (team_id[team_id["Last Year"] == "Present"]).reset_index(drop=True)

        # batting stats url
        bat_url = f"https://www.baseball-reference.com/leagues/majors/{season_year}-standard-batting.shtml"
        adv_bat_url = f"https://www.baseball-reference.com/leagues/majors/{season_year}-advanced-batting.shtml"
        # find_bat_tables = findTables(adv_bat_url)  # find the associated tables

        # player batting
        player_bat = pd.read_html(bat_url)[1].rename(columns={"Player": "Name"})
        player_bat = player_bat[
            player_bat["Rk"].notnull()
            & ~(player_bat["Lg"].str.contains("LG", na=False))
        ]
        player_bat = player_bat.rename(
            columns={"Player": "Name", "Team": "Tm"}
        )  # fix column naming bug
        for i in player_bat.index:
            for charc in special_charc:
                player_bat.loc[i, "Name"] = (
                    unidecode.unidecode(player_bat["Name"][i])
                    .replace(charc, "")
                    .replace("Ã­­", "i")
                    .replace("Ã©", "e")
                    .replace("Ã\xad", "i")
                    .replace("Ã¡", "a")
                    .replace("Ã±", "n")
                    .replace("Ã³", "o")
                    .replace("Ãº", "u")
                    .replace("Ã\x81", "A")
                    .replace("Ã\x93", "O")
                    .replace(".", "")
                    .strip()
                )

        tmp_adv_bat = pd.read_html(adv_bat_url)[1]
        # need to piece together the advanced batting df
        adv_player_bat = pd.concat(
            [
                tmp_adv_bat["Unnamed: 0_level_0"][["Rk"]],
                tmp_adv_bat["Unnamed: 1_level_0"][["Player"]].rename(
                    columns={"Player": "Name"}
                ),
                tmp_adv_bat["Unnamed: 3_level_0"][["Team"]].rename(
                    columns={"Team": "Tm"}
                ),
                tmp_adv_bat["Unnamed: 4_level_0"][["Lg"]],
                tmp_adv_bat["Batted Ball"][["GB%", "FB%", "LD%"]],
                tmp_adv_bat["Batting Ratios"][["SO%", "BB%", "HR%"]],
            ],
            axis=1,
        )
        adv_player_bat = adv_player_bat[
            adv_player_bat["Rk"].notnull()
            & ~(adv_player_bat["Lg"].str.lower().str.contains("lg", na=False))
        ]
        for i in adv_player_bat.index:
            for charc in special_charc:
                adv_player_bat.loc[i, "Name"] = (
                    unidecode.unidecode(adv_player_bat["Name"][i])
                    .replace(charc, "")
                    .replace("Ã­­", "i")
                    .replace("Ã©", "e")
                    .replace("Ã\xad", "i")
                    .replace("Ã¡", "a")
                    .replace("Ã±", "n")
                    .replace("Ã³", "o")
                    .replace("Ãº", "u")
                    .replace("Ã\x81", "A")
                    .replace("Ã\x93", "O")
                    .replace(".", "")
                    .strip()
                )
        adv_player_bat = adv_player_bat[~(adv_player_bat["Rk"] == "Rk")]

        player_bat["OBP"] = player_bat["OBP"].replace("", ".000")
        player_bat["SLG"] = player_bat["SLG"].replace("", ".000")
        player_bat = player_bat.astype(
            {
                "OBP": float,
                "SLG": float,
                "PA": int,
                "AB": int,
                "H": int,
                "2B": int,
                "3B": int,
                "HR": int,
            }
        )

        adv_player_bat["GB%"] = adv_player_bat["GB%"] / 100
        adv_player_bat["FB%"] = adv_player_bat["FB%"] / 100
        adv_player_bat["LD%"] = adv_player_bat["LD%"] / 100
        adv_player_bat["SO%"] = adv_player_bat["SO%"] / 100
        adv_player_bat["BB%"] = adv_player_bat["BB%"] / 100
        adv_player_bat["HR%"] = adv_player_bat["HR%"] / 100
        adv_player_bat = adv_player_bat.astype(
            {
                "GB%": float,
                "FB%": float,
                "LD%": float,
                "SO%": float,
                "BB%": float,
                "HR%": float,
            }
        )

        player_bat_df = (
            player_bat.groupby(["Name"])
            .agg(
                Tm=("Tm", "last"),
                OBP=("OBP", "median"),
                SLG=("SLG", "median"),
                pa=("PA", "sum"),
                abs=("AB", "sum"),
                hits=("H", "sum"),
                doubles=("2B", "sum"),
                triples=("3B", "sum"),
                homers=("HR", "sum"),
            )
            .reset_index()
        )
        player_bat_df["singles"] = player_bat_df["hits"].astype(int) - (
            player_bat_df["doubles"].astype(int)
            + player_bat_df["triples"].astype(int)
            + player_bat_df["homers"].astype(int)
        )
        # add in advanced batting for GO%, FO%, SO%, BB%
        adv_player_bat_df = (
            adv_player_bat.groupby(["Name"])
            .agg(
                Tm=("Tm", "last"),
                GO=("GB%", "median"),
                FO=("FB%", "median"),
                SO=("SO%", "median"),
                BB=("BB%", "median"),
            )
            .reset_index()
        )

        player_bat_df["1B"] = player_bat_df["singles"].astype(int) / player_bat_df[
            "hits"
        ].astype(int)
        player_bat_df["2B"] = player_bat_df["doubles"].astype(int) / player_bat_df[
            "hits"
        ].astype(int)
        player_bat_df["3B"] = player_bat_df["triples"].astype(int) / player_bat_df[
            "hits"
        ].astype(int)
        player_bat_df["HR"] = player_bat_df["homers"].astype(int) / player_bat_df[
            "hits"
        ].astype(int)

        player_bat_df = player_bat_df.rename(
            columns={
                "pa": "PA",
                "hits": "H",
            }
        ).fillna(0)
        player_bat_df = player_bat_df.astype(
            {"1B": float, "2B": float, "3B": float, "HR": float}
        )
        # merge standard and advanced batting
        player_bat_df = player_bat_df.merge(
            adv_player_bat_df, how="left", on=["Name", "Tm"]
        )
        player_bat_df = player_bat_df.fillna(0)

        """
            PLAYER PITCHING
        """
        # pitching stats url
        pitch_url = f"https://www.baseball-reference.com/leagues/majors/{season_year}-standard-pitching.shtml"

        # player pitching
        player_pitch = pd.read_html(pitch_url)[1]
        player_pitch = player_pitch[
            player_pitch["Rk"].notnull()
            & ~(player_pitch["Lg"].str.contains("LG", na=False))
        ]
        player_pitch = player_pitch.rename(
            columns={"Player": "Name", "Team": "Tm"}
        )  # fix column naming bug
        for i in player_pitch.index:
            for charc in special_charc:
                player_pitch.loc[i, "Name"] = (
                    unidecode.unidecode(player_pitch["Name"][i])
                    .replace(charc, "")
                    .replace("Ã­­", "i")
                    .replace("Ã©", "e")
                    .replace("Ã\xad", "i")
                    .replace("Ã¡", "a")
                    .replace("Ã±", "n")
                    .replace("Ã³", "o")
                    .replace("Ãº", "u")
                    .replace("Ã\x81", "A")
                    .replace("Ã\x93", "O")
                    .replace(".", "")
                    .strip()
                )

        # creating a balls/strikes calculation
        player_pitch = player_pitch.astype(
            {"SO": int, "H": int, "BB": int, "IBB": int, "WP": int, "HBP": int}
        )
        player_pitch["strikes"] = (player_pitch["SO"] * 3) + (player_pitch["H"])
        player_pitch["balls"] = (
            (player_pitch["BB"] * 4)
            + (player_pitch["IBB"] * 4)
            + (player_pitch["WP"])
            + (player_pitch["HBP"])
        )
        player_pitch["K%"] = (
            player_pitch["strikes"] / (player_pitch["strikes"] + player_pitch["balls"])
        ).fillna(0.15)
        player_pitch.loc[player_pitch["K%"] <= 0.15, "K%"] = 0.15
        player_pitch.loc[player_pitch["K%"] >= 0.85, "K%"] = 0.85

        player_pitch["WHIP"] = player_pitch["WHIP"].replace("", "0.000")
        player_pitch["ERA"] = player_pitch["ERA"].replace("", "0.00")
        player_pitch = player_pitch.astype({"WHIP": float, "ERA": float})
        player_pitch_df = (
            player_pitch.groupby(["Name"])
            .agg(
                Tm=("Tm", "last"),
                WHIP=("WHIP", "median"),
                ERA=("ERA", "median"),
                Kpct=("K%", "median"),
            )
            .rename(columns={"Kpct": "K%"})
            .reset_index()
        )

        """
            TEAM FIELDING
        """
        # fielding stats url
        field_url = f"https://www.baseball-reference.com/leagues/majors/{season_year}-standard-fielding.shtml"

        # team fielding
        team_field = pd.read_html(field_url)[0]
        # team name dict
        team_name_dict = {
            "Arizona Diamondbacks": "ARI",
            "Atlanta Braves": "ATL",
            "Baltimore Orioles": "BAL",
            "Boston Red Sox": "BOS",
            "Chicago Cubs": "CHC",
            "Chicago White Sox": "CWS",
            "Cincinnati Reds": "CIN",
            "Cleveland Guardians": "CLE",
            "Colorado Rockies": "COL",
            "Detroit Tigers": "DET",
            "Houston Astros": "HOU",
            "Kansas City Royals": "KCR",
            "Los Angeles Angels": "LAA",
            "Los Angeles Dodgers": "LAD",
            "Miami Marlins": "MIA",
            "Milwaukee Brewers": "MIL",
            "Minnesota Twins": "MIN",
            "New York Mets": "NYM",
            "New York Yankees": "NYY",
            "Oakland Athletics": "OAK",
            "Philadelphia Phillies": "PHI",
            "Pittsburgh Pirates": "PIT",
            "San Diego Padres": "SDP",
            "Seattle Mariners": "SEA",
            "San Francisco Giants": "SFG",
            "St. Louis Cardinals": "STL",
            "Tampa Bay Rays": "TBR",
            "Texas Rangers": "TEX",
            "Toronto Blue Jays": "TOR",
            "Washington Nationals": "WSN",
        }
        team_field["Tm_Abbv"] = team_field["Tm"].map(team_name_dict)
        team_field_df = team_field[team_field["Tm_Abbv"].notna()][
            ["Tm_Abbv", "Fld%"]
        ].rename(columns={"Tm_Abbv": "Tm"})
        team_field_df['Fld%'] = team_field_df['Fld%'].astype(float)

        # add years
        player_bat_df["year"] = season_year
        player_pitch_df["year"] = season_year
        team_field_df["year"] = season_year

        full_player_bat_df = (
            pd.concat([full_player_bat_df, player_bat_df])
            .sort_values(by=["Name", "year"])
            .reset_index(drop=True)
        )
        full_player_pitch_df = (
            pd.concat([full_player_pitch_df, player_pitch_df])
            .sort_values(by=["Name", "year"])
            .reset_index(drop=True)
        )
        full_team_field_df = (
            pd.concat([full_team_field_df, team_field_df])
            .sort_values(by=["Tm", "year"])
            .reset_index(drop=True)
        )

        # sleep 10 seconds after each data pull
        time.sleep(10)

    # use weighted avg for all metrics
    player_bat_df = (
        full_player_bat_df.sort_values(by="year")
        .groupby(["Name"])
        .agg(
            Tm=("Tm", "last"),
        )
        .reset_index()
    )
    for metric in [
        "OBP",
        "SLG",
        "PA",
        "H",
        "1B",
        "2B",
        "3B",
        "HR",
        "GO",
        "FO",
        "SO",
        "BB",
    ]:
        logger.info(f"Running: {metric}")
        player_bat_df = player_bat_df.merge(
            player_weighted_avg(season_years, full_player_bat_df, metric),
            how="inner",
            on="Name",
        ).reset_index(drop=True)

    player_pitch_df = (
        full_player_pitch_df.sort_values(by="year")
        .groupby(["Name"])
        .agg(
            Tm=("Tm", "last"),
        )
        .reset_index()
    )
    for metric in ["WHIP", "ERA", "K%"]:
        logger.info(f"Running: {metric}")
        player_pitch_df = player_pitch_df.merge(
            player_weighted_avg(season_years, full_player_pitch_df, metric),
            how="inner",
            on="Name",
        ).reset_index(drop=True)

    for metric in ["Fld%"]:
        logger.info(f"Running: {metric}")
        team_field_df = team_weighted_avg(
            season_years, full_team_field_df, metric
        ).reset_index(drop=True)

    lg_whip = player_pitch_df["WHIP"].median()
    player_pitch_df["WHIP"] = player_pitch_df["WHIP"] / lg_whip
    player_pitch_df.loc[player_pitch_df["WHIP"] > 1, "WHIP"] = 1

    return [player_bat_df, player_pitch_df, team_field_df]
