#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt


def winexp(t1, t2):
    we2 = 1 / (1 + 10 ** ((t1 - t2) / 400))  # winning expectancy of team 2
    we1 = 1-we2
    return round(we1, 2), round(we2, 2)


def webscrape(week, tab):
    tab2 = tab[week - 1]
    tab2.dropna(inplace=True)  # cleaning data
    tab2.drop(tab2.columns[[3, 4]], axis=1, inplace=True)  # removing NaNs
    tab2.reset_index(drop=True, inplace=True)
    tab2.columns = ['Team1', 'Score1', 'Score2', 'Team2']
    return tab2


def elocalc():
    k = 47  # k-factor
    while True:
        region = input("Ranking której ligi chcesz modyfikować? ")
        try:
            season = pd.read_html('https://lol.fandom.com/%s/2021_Season/Spring_Season' % region,
                                  # getting table with results
                                  attrs={'class': 'wikitable2 matchlist'})
        except Exception as e:
            print(e)
            continue
        break
    df = pd.DataFrame(index=['Rating'])
    week = 1
    while True:
        try:
            results = webscrape(week, season)
        except (IndexError, ValueError):
            break
        for i in range(len(results.index)):
            team1 = results.loc[i, 'Team1'].replace('\u2060', '')
            team2 = results.loc[i, 'Team2'].replace('\u2060', '')
            if team1 not in df.columns:
                df[team1] = 1000
            if team2 not in df.columns:
                df[team2] = 1000
            win1, win2 = winexp(df.loc['Rating', team1], df.loc['Rating', team2])

            if results.loc[i, 'Score1'] > results.loc[i, 'Score2']:
                df.loc['Rating', team1] += k*(1-win1)
                df.loc['Rating', team2] += k*(0-win2)
            else:
                df.loc['Rating', team1] += k*(0-win1)
                df.loc['Rating', team2] += k*(1-win2)
        week += 1

    df = df.T
    df = df.sort_values(by='Rating', ascending=False)
    dfprint = df.reset_index()  # dataframe for pretty print
    dfprint.index += 1
    dfprint.rename(columns={'index': 'Team'}, inplace=True)
    df = df.round(1)
    print(tabulate(dfprint, headers='keys', tablefmt="fancy_grid", floatfmt='.1f'))
    df.to_csv(region + '.csv', index='True')


def stats():
    while True:
        region = input("Dla której ligi chcesz statystyki: ").upper()
        try:
            df = pd.read_csv(region + '.csv', index_col=0)
        except FileNotFoundError as e:
            print(e)
            continue
        break

    print(df.describe())


def main():
    print("""\t\t\tWitaj w programie ESPORTS ELO
    Co chcesz zrobić?
    1. Policzyć ranking ELO
    2. Inne
        """)
    option = int(input(""))
    if option == 1:
        elocalc()
    elif option == 2:
        stats()

    input()


main()
