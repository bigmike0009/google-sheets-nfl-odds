import requests
import json
from datetime import datetime, timedelta
import dateutil.tz
BOOKMAP = {'DraftKings':'dk', 'Bovada':'bov', 'FanDuel':'fd'}

def format_to_sheets():
    res=fetchOdds()
    resArray = []
    for matchup in res:
        spreadBook = BOOKMAP[res[matchup]["spreads"]["book"]]
        mlBook = BOOKMAP[res[matchup]["ml"]["book"]]
        overBook = BOOKMAP[res[matchup]["totals"]["book"]]

        spread = res[matchup]['spreads']['amount']
        spread = '+' + str(spread) if spread > 0 else str(spread)
        spreadLine = matchup.replace('@',spread + ' @') + f' ({spreadBook})'

        ml = res[matchup]['ml']['amount']
        ml = '\'+' + str(ml) if ml > 0 else str(ml)

        over = res[matchup]['totals']['amount']

        resArray.append([matchup.split( ' @ ')[0], matchup.split( ' @ ')[1], spreadLine, ml + f' ({mlBook})', str(over) + f' ({overBook})', res[matchup]['kickoff']])
    print(resArray)
    return resArray

def dirty_utc_to_time(naive):
    clean = datetime.fromisoformat(naive[:-1])
    adjustedTimeZone = clean.replace(tzinfo=dateutil.tz.gettz(
        'UTC')).astimezone(dateutil.tz.gettz('US/Eastern'))
    return adjustedTimeZone

def fetchOdds(sport_key='americanfootball_nfl'):
    
    upcomingMatchups = requestOddsApi(sport_key)
    
    

    resultDict =  {}

    for matchup in upcomingMatchups:
        home_team = matchup['home_team']
        away_team = matchup['away_team']

        gameTime = dirty_utc_to_time(matchup['commence_time'])

        matchID = away_team + ' @ ' + home_team 
        resultDict[matchID] = {'kickoff':gameTime.strftime('%a %I:%M%p')}

        bestOdds = {'h2h':{'BookAway': 'N/A', 'OddsAway': -
                    99999, 'BookHome': 'N/A', 'OddsHome': -99999},
                    'spreads':{'BookAway': 'N/A', 'OddsAway': -
                    99999},
                    'totals':{'BookOver': 'N/A', 'OddsOver': 
                    99999, 'BookUnder': 'N/A', 'OddsUnder': -99999}}

        for sBook in matchup['bookmakers']:

            # home ML odds
            for mkt in sBook['markets']:
                if mkt['outcomes'][0]['name'] == home_team:
                    home = mkt['outcomes'][0]
                    # away ML odds
                    away = mkt['outcomes'][1]
                else:
                    home = mkt['outcomes'][1]
                    away = mkt['outcomes'][0]




                

                if mkt['key'] == 'h2h':
                # if home ml is less than 10 min old and beats the high score
                    if home['price'] >= bestOdds[mkt['key']]['OddsHome']:
                        bestOdds[mkt['key']]['BookHome'] = sBook['title']
                        bestOdds[mkt['key']]['OddsHome'] = home['price']
                        # bestOdds[mkt['key']]['UpdatedHome'] = dirty_utc_to_time(sBook['last_update']).strftime('%I:%M %p +%Ss')

                    if away['price'] >= bestOdds[mkt['key']]['OddsAway']:
                        bestOdds[mkt['key']]['BookAway'] = sBook['title']
                        bestOdds[mkt['key']]['OddsAway'] = away['price']
                elif mkt['key'] == 'spreads':
                    if away['point'] >= bestOdds[mkt['key']]['OddsAway']:
                        bestOdds[mkt['key']]['BookAway'] = sBook['title']
                        bestOdds[mkt['key']]['OddsAway'] = away['point']  
                else:
                    if away['point'] <= bestOdds[mkt['key']]['OddsOver']:
                        bestOdds[mkt['key']]['BookOver'] = sBook['title']
                        bestOdds[mkt['key']]['OddsOver'] = away['point']  

        
        if bestOdds['h2h']['OddsHome'] > bestOdds['h2h']['OddsAway']:
            #Home team is a DAWG
            resultDict[matchID].update({'ml':{'amount': bestOdds['h2h']['OddsHome'], 'book': bestOdds['h2h']['BookHome']}})
        else:
            #Away team is a DAWG
            resultDict[matchID].update({'ml':{'amount': bestOdds['h2h']['OddsAway'], 'book': bestOdds['h2h']['BookAway']}})

        resultDict[matchID].update({'spreads':{'amount':bestOdds['spreads']['OddsAway'], 'book':bestOdds['spreads']['BookAway']}})
        resultDict[matchID].update({'totals':{'amount':bestOdds['totals']['OddsOver'], 'book':bestOdds['totals']['BookOver']}})

    return resultDict
        # record odds that meet the following conditions
        

def requestOddsApi(sport_key='football_nfl', market='h2h,spreads,totals'):
    
    api_key = 'e26d8f8a7475a9a7ce69156c4f3d3d8e'
    #TODO free subscription api key, but still upload this to GCP secret manager
    day_of_week = datetime.now().weekday()
    days_until_next_week_of_football = 9 - day_of_week


    start_of_next_week = datetime.now() + timedelta(days=days_until_next_week_of_football)
    ISOTIME=start_of_next_week.strftime('%Y-%m-%dT23:59:59Z')

    request_string = 'https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={apkey}&regions=us&markets={mkt}&oddsFormat=american&bookmakers=fanduel,draftkings,bovada&commenceTimeTo={endDT}'.format(
        apkey=api_key,            sport=sport_key,
        mkt=market,  endDT=ISOTIME# h2h | spreads | totals
    )
    odds_response = requests.get(request_string)
    gamesArray = json.loads(odds_response.text)
    
    return gamesArray   
