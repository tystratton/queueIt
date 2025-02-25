# from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
import asyncio
import json
from datetime import datetime, timedelta
# import requests
# from urllib.parse import quote

# Super verbose debugging
print("Current working directory:", os.getcwd())
print("Loading environment variables...")
load_dotenv()
# api_key = os.getenv('RIOT_API_KEY')

# print("\nAPI Key Verification:")
# print(f"Key loaded: {'Yes' if api_key else 'No'}")
# print(f"Key starts with RGAPI-: {'Yes' if api_key.startswith('RGAPI-') else 'No'}")
# print(f"Key length: {len(api_key)} characters")

# if not api_key:
#     raise ValueError("No Riot API key found in .env file! Please add RIOT_API_KEY=RGAPI-your-key-here")

class LeagueBetting:
    def __init__(self):
        # self.api_key = api_key
        # self.game_name = "teaxthree"
        # self.tag_line = "ARAM"
        # self.puuid = "-4cF64jJPR1uNK8sIP4z9KDiKxj8wFaKUYzhVk5tndy9IHXMoSXaJWZVpT83d06Pz9APJK29fbt1qg"
        # self.headers = {"X-Riot-Token": self.api_key}
        # self.current_game = None
        # self.last_checked_match = None
        self.active_bets = {}
        self.points_file = 'channel_points.json'
        self.load_points()
        self.betting_open = False
        self.last_game_id = None

    def load_points(self):
        """Load channel points from file"""
        try:
            with open(self.points_file, 'r') as f:
                self.channel_points = json.load(f)
        except FileNotFoundError:
            self.channel_points = {}
            self.save_points()

    def save_points(self):
        """Save channel points to file"""
        with open(self.points_file, 'w') as f:
            json.dump(self.channel_points, f)

    def get_points(self, user_id):
        """Get user's points, create entry if doesn't exist"""
        if user_id not in self.channel_points:
            self.channel_points[user_id] = 1000  # Starting points
            self.save_points()
        return self.channel_points[user_id]

    # async def check_current_game(self):
    #     """Check if player is in an active game"""
    #     try:
    #         # Get most recent match
    #         url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.puuid}/ids?start=0&count=1"
    #         response = requests.get(url, headers=self.headers)
            
    #         if response.status_code == 200:
    #             matches = response.json()
    #             if matches:
    #                 latest_match = matches[0]
                    
    #                 # If this is our first check, just store the match ID
    #                 if self.last_checked_match is None:
    #                     self.last_checked_match = latest_match
    #                     return False
                    
    #                 # Check if this is a new match (different from last checked)
    #                 if latest_match != self.last_checked_match:
    #                     # Get match details to verify it's recent
    #                     match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{latest_match}"
    #                     match_response = requests.get(match_url, headers=self.headers)
                        
    #                     if match_response.status_code == 200:
    #                         match_data = match_response.json()
    #                         game_end_timestamp = match_data['info']['gameEndTimestamp']
    #                         game_end_time = datetime.fromtimestamp(game_end_timestamp / 1000)
                            
    #                         # Only consider it a new game if it ended in the last 5 minutes
    #                         if datetime.now() - game_end_time < timedelta(minutes=5):
    #                             self.last_checked_match = latest_match
    #                             self.current_game = latest_match
    #                             return True
            
    #         return False
            
    #     except Exception as e:
    #         print(f"Error checking current game: {e}")
    #         return False

    def place_bet(self, user_id, amount, prediction):
        """Place a bet on the current game"""
        if not self.current_game:
            return "No active game to bet on!"
        
        if user_id not in self.channel_points:
            self.channel_points[user_id] = 1000  # Starting points
            
        if amount > self.channel_points[user_id]:
            return f"Not enough points! You have {self.channel_points[user_id]} points."
            
        self.active_bets[user_id] = {
            "amount": amount,
            "prediction": prediction,
            "timestamp": datetime.now().timestamp()
        }
        
        self.channel_points[user_id] -= amount
        self.save_points()
        
        return f"Bet placed: {amount} points on {prediction}"

    def process_game_result(self, won: bool):
        """Process all bets after game ends"""
        payouts = []
        for user_id, bet in self.active_bets.items():
            bet_won = (bet["prediction"].lower() == 'win') == won
            if bet_won:
                payout = bet["amount"] * 2
                self.channel_points[user_id] += payout
                payouts.append(f"{user_id} won {payout} points!")
            else:
                payouts.append(f"{user_id} lost {bet['amount']} points!")

        self.save_points()
        self.active_bets = {}  # Clear bets
        return payouts

    # async def monitor_game_state(self):
    #     """Monitor for new games and results"""
    #     while True:
    #         try:
    #             summoner = self.lol_watcher.summoner.by_name(self.region, self.summoner_name)
                
    #             try:
    #                 # Check if in game
    #                 spectator = self.lol_watcher.spectator.by_summoner(self.region, summoner['id'])
    #                 game_id = spectator['gameId']
                    
    #                 # If this is a new game
    #                 if game_id != self.last_game_id:
    #                     self.last_game_id = game_id
    #                     self.betting_open = True
    #                     self.current_game = game_id
    #                     return "BETTING_OPEN"  # Signal to announce betting is open
                        
    #             except Exception as e:
    #                 # Not in game, check if we need to close previous game
    #                 if self.current_game:
    #                     # Get match history to check result
    #                     match_history = self.lol_watcher.match.matchlist_by_puuid(
    #                         self.region, 
    #                         summoner['puuid'],
    #                         count=1
    #                     )
    #                     if match_history:
    #                         # Process game result
    #                         match = self.lol_watcher.match.by_id(self.region, match_history[0])
    #                         # Find player in match and check if won
    #                         for participant in match['info']['participants']:
    #                             if participant['summonerName'].lower() == self.summoner_name.lower():
    #                                 won = participant['win']
    #                                 self.betting_open = False
    #                                 results = self.process_game_result(won)
    #                                 return f"GAME_ENDED:{'WIN' if won else 'LOSS'}"
                
    #         except Exception as e:
    #             print(f"Error monitoring game state: {e}")
            
    #         await asyncio.sleep(30)  # Check every 30 seconds

    # async def test_connection(self):
    #     """Test Riot API endpoints"""
    #     try:
    #         print("\nTesting Riot API endpoints...")
            
    #         base_url = f"https://{self.region}.api.riotgames.com"
    #         headers = {
    #             "X-Riot-Token": self.api_key
    #         }

    #         # First get platform status (this worked before)
    #         print("\n1. Testing platform status...")
    #         status_url = f"{base_url}/lol/status/v4/platform-data"
    #         response = requests.get(status_url, headers=headers)
    #         print(f"Status code: {response.status_code}")

    #         # Now try summoner lookup with proper URL encoding
    #         print("\n2. Testing summoner lookup...")
    #         encoded_name = quote(self.summoner_name)
    #         summoner_url = f"{base_url}/lol/summoner/v4/summoners/by-name/{encoded_name}"
    #         print(f"Making request to: {summoner_url}")
            
    #         response = requests.get(summoner_url, headers=headers)
    #         print(f"Status code: {response.status_code}")
    #         print(f"Response: {response.text}")

    #         if response.status_code == 200:
    #             data = response.json()
    #             print("\nSuccess! Found summoner:")
    #             print(f"Name: {data.get('name')}")
    #             print(f"Level: {data.get('summonerLevel')}")
    #             print(f"PUUID: {data.get('puuid')}")
    #             return True
    #         else:
    #             print(f"Failed to get summoner data: {response.text}")
    #             return False
                
    #     except Exception as e:
    #         print(f"\nError making request: {str(e)}")
    #         return False

# async def test_betting():
#     betting = LeagueBetting()
#     is_in_game = await betting.check_current_game()
#     print(f"In game: {is_in_game}")
    
#     if is_in_game:
#         # Test bet
#         result = betting.place_bet("test_user", 100, "win")
#         print(f"Bet result: {result}")
        
#         # Test points
#         points = betting.get_points("test_user")
#         print(f"User points: {points}")

# if __name__ == "__main__":
#     asyncio.run(test_betting())
