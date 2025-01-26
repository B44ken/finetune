# finetune
finetune gpt4o to talk like your discord logs.

## usage
get a discord log of your chats via https://github.com/Tyrrrz/DiscordChatExporter
```bash
./DiscordChatExporter.Cli export -c $CHANNEL_ID -t $DISCORD_TOKEN -f json -o chats.json
```
parse and create a finetune
```
./main.py $DISCORD_USER chats.json $OPENAI_KEY
```
the rest must be done mostly manually.
- go to your discord channel, open the console
- paste in `scrape.js` and copy the output chat logs
- go to https://platform.openai.com/playground/chat, select your finetune
- paste in the chat logs, and paste `continue the conversation. you are $DISCORD_USER.` (supply) into the system prompt
- run your stupid fine tune