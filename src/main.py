import functions_framework
from google.oauth2 import service_account
from googleapiclient.discovery import build
import oddsApi as oddsApi
from datetime import datetime, timedelta

OPENINGWEEK=datetime.strptime('5 Sep 2024', '%d %b %Y')

CURRDT = datetime.now()
CURRWEEK = int(((CURRDT - OPENINGWEEK).days) / 7) + 1

@functions_framework.http
def hello_http(request):
    result=''
    spreadsheet_id = '1dlcPCLbLOma94nI2j6HJ71_ubqVKR7uBze3KSo7rsUI'
    # For example:
    # spreadsheet_id = "8VaaiCuZ2q09IVndzU54s1RtxQreAxgFNaUPf9su5hK0"

    credentials = service_account.Credentials.from_service_account_file("key.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=credentials)

    if does_sheet_exist(service, spreadsheet_id):
            return 'ERROR - Sheet already exists for Week ' + str(CURRWEEK)


    newSheetID = create_new_sheet(service, spreadsheet_id)

    footballOdds = oddsApi.format_to_sheets()
    numGames = len(footballOdds)

    result = append_new_rows(footballOdds, service, spreadsheet_id)

    result = copy_formula_for_rows(service, newSheetID, numGames, spreadsheet_id)

    result = add_dropdowns(service, newSheetID, spreadsheet_id, numGames)
    

    

    result = service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f'Week {CURRWEEK}!A2:M2'
    ).execute()


    print(result)
    return 'Week ' + str(CURRWEEK) + ' LOCK sheet has been created'

def create_new_sheet(service, spreadsheet_id):
    request = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=[], includeGridData=False)
    sheet_props = request.execute()
    new_week_sheet_id=''

    for sheet in sheet_props['sheets']:
        if sheet['properties']['title'] == 'template':
            new_week_sheet_id = sheet['properties']['sheetId']
            result = service.spreadsheets().sheets().copyTo(spreadsheetId=spreadsheet_id, sheetId=sheet['properties']['sheetId'], body={'destinationSpreadsheetId':spreadsheet_id}).execute()
            print(result)
            newSheetID = result['sheetId']
            
            body={ "requests":[
              {"updateSheetProperties": {
            "properties": {
                "sheetId": sheet['properties']['sheetId'],
                "title": 'Week '+str(CURRWEEK)
            },
            "fields": "title",
        }},
                {"updateSheetProperties": {
            "properties": {
                "sheetId": newSheetID,
                "title": 'template'
            },
            "fields": "title",
        }}
        
            ]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
            return new_week_sheet_id
    return 'ERROR'

def append_new_rows(gameData, service, spreadsheet_id):
    body = { # Data within a range of the spreadsheet.
    "values": gameData
    }
    return service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f'Week {CURRWEEK}!A2:G2',
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

def copy_formula_for_rows(service, newSheetID, numGames, spreadsheet_id):
    body = {
  "requests": [
    {
      "copyPaste": {
        "source": {
          "sheetId": newSheetID,
          "startRowIndex": 1,
          "endRowIndex": 2,
          "startColumnIndex": 11,
          "endColumnIndex": 12
        },
        "destination": {
          "sheetId": newSheetID,
          "startRowIndex": 2,
          "endRowIndex": 2 + numGames,
          "startColumnIndex": 11,
          "endColumnIndex": 12
        },
        "pasteType": "PASTE_FORMULA",
        "pasteOrientation": "NORMAL"
      }
    }
  ]
}
    return service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

def add_dropdowns(service, newSheetID, spreadsheet_id, numgames):
    requests = []
    for i in range(2, 2 + numgames):
        gridRange = {
            "sheetId": newSheetID,
            "startRowIndex": i,
            "endRowIndex": i+1,
            "startColumnIndex": 7,
            "endColumnIndex": 11
        }

        requests.append({
                "setDataValidation": {
                    "range": gridRange,
                    "rule": {
                        "condition": {
                            "type": 'ONE_OF_RANGE',
                            "values": [{'userEnteredValue':f'=\'Week {CURRWEEK}\'!A{i+1}:B{i+1}'}],
                        },
                        "showCustomUi": True,
                        "strict": False
                    }
                }
            })


    return service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests':requests}).execute()

def does_sheet_exist(service, spreadsheet_id):
    try:
        service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,range=f'Week {CURRWEEK}!A1:B1').execute()
        return True
    except:
        return False