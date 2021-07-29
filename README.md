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
pip install -r requirements.txt
```

Navigate to the directory where you clone this project.
Create a .env file in the following format.

```txt
DISCORD_TOKEN={your_bot_token}
DISCORD_GUILD={your_server}
WORDS_API_KEY={your key}
```

This is the environment variable(s) that the bot accesses the BOT_TOKEN and GUILD from.

### Game Settings

*On progress*

### Commands

For more information see our help menu

## Contribution

Pull requests are accepted! Please open an issue if you find any bugs, or have any idea for a feature. Feedbacks are welcomed

## License

GNU Affero General Public License 3.0
