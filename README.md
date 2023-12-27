# Lock of the Week

For every NFL sunday in the last half decade, 3 of my closest friends have put our heads together in pursuits of striking it big by picking our 4 favorite teams in the 15 matchups of the week. Coined "The Lock of the Week", this process evolved and refined itself with time, to where now the 4 of us all hop onto the shared spreadsheet like clockwork at 11AM on sunday morning. Some of the tasks include researching all the  vegas predictions for the game, analyzing kickoff time, weather conditions, injury report and shopping between competing sportsbooks.

Realizing what a time drain this process had become, I wasted no time combining my love of software solutions and sports together. Now we are able to focus on making the important decisons, with the most information possible

![Project](https://zak-rentals.s3.amazonaws.com/before.png)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Infrastructure](#Infrastructure)
- [Acknowledgements](#Acknowledgements)


## Introduction

This is a python solution deployed to GCPs serverless cloud run service. 
Every sunday during football season, it populates a new tab in the specified google spreadsheet with all the required information.

## Features

- Seamless integration with google's graph api
- Pulling live sports and odds data from an API data feed
- Custom formatting for data validations, readability and visualization
- Formulas and conditional formatting to allow for blind and highlighting winning picks
- Shopping for the most competitives line on each event

## Infrastructure

Code is deployed to GCP leveraging the continuous deployment feature of cloud run.
Scheduling and containerization is configured in google cloud functions service.
This container is currently running **Python 3.9** 
A cloud run role must be granted access to our google sheet explicitly

## Acknowledgements

[Odds API](https://the-odds-api.com/) for being reliable and accurate in providng most current vegas odds
