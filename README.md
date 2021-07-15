# Shiritori_bot
Shiritori (しりとり) is a Japanese word game in which the players are required to say a word which begins with the final kana of the previous word.
This is my take on the Shiritori bot but in English.

## Rules
Players must submit a word in the chat which begins with the final letter of the previous word.
Players can not repeat each other's words and also can not repeat their own words.
A word violates said rules or has no meaning is considered an invalid word.

If a player submit 3 invalid words through out the game, they will be kicked.
If a player is out of time, they wil be kicked.

## Usage
### Setup
```bash
$ pip install -r requirements.txt
```

Navigate to the directory where you clone this project.
Create a .env file in the following format.

```
DISCORD_TOKEN={your_bot_token}
DISCORD_GUILD={your_server}
```

This is the environment variable(s) that the bot accesses the BOT_TOKEN and GUILD from.

### Game Settings

In class Players, you can change the `invalid_left` variable, which determined the maximum errors a player can make.

```python
class Players:
    """a class to represent players"""
    name = ""
    score = 0
    invalid_left = 3
    time_left = 0
    timer_state = 0
    timer = threading.Timer
    start_time = 0
```

Also, you can change the timer here:

```python
async def create(ctx, game_type: str):
    """create a game by selecting the game mode"""
    global DEFAULT_TIME
    if game_type == "bullet":
        DEFAULT_TIME = 60
    elif game_type == "blitz":
        DEFAULT_TIME = 180
    elif game_type == "casual":
        DEFAULT_TIME = 1800
```

You can customize `DEFAULT_TIME` however you like. I'm using chess-style timer countdown.

### Commands
For more information see our help menu

## Contribution
Pull requests are accepted! Please open an issue if you find any bugs, or have any idea for a feature. Feedbacks are welcomed

## License
Apache License 2.0











