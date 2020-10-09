import auths
import discord
import yfinance as yf
from api import Discord
from api import PredictIt

pi_api = PredictIt()
discord_api = Discord(pi_api)
client = discord.Client()
stats = {"users": {}, "commands": {}}


@client.event
async def on_message(message):
    if message.author == client.user:
        pass
    elif (
        message.content.startswith(",Help")
        or message.content.startswith(",help")
        or message.content.startswith(",h")
    ):
        stats["commands"]["help"] = stats["commands"].get("help", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        title = "Here are the commands I can perform:\n"
        msg = ",h brings up this message.\n"
        msg += ",r figures out whether a market has negative risk or not. The keyword 'all' searches all the markets.\n"
        msg += ",b shows the prices for each bin in a market.\n"
        msg += ",v compares the cost of buying Yes and buying no on everything else.\n"
        msg += ",- gets all the markets that contain the input in the title.\n"
        msg += (
            ",. gets all the markets that contain the input in the one of the bins.\n"
        )
        msg += ",o gets the volume of the contracts in a specific market.\n"
        msg += (
            ",rcp gets the current rcp averages for the nation or individual states.\n"
        )
        msg += ",stock or ,s gets the last traded price of the indicated ticker. \n"
        msg += "\n"
        msg += "This bot took a while to make, and as a broke college student, I'd really appreciate a donation if like the bot or find it useful.\n"
        msg += "    Bitcoin: \n    bc1qxmm7l2vhema687hrvle3yyp04h6svzy8tkk8sg\n"
        msg += "    PayPay, Venmo, etc: \n    PM @crazycrabman#2555\n"
        msg += "The bot is running on AWS, so it should be online 24/7. If it isn't, you have an idea for another command, or just want to chat about this bot, PM @crazycrabman#2555\n"
        print("Help")
        print(message.author)
        embed = discord.Embed(title=title, description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",murder") or message.content.startswith(",kill"):
        msg = "oh no you have killed me\n"
        msg += "I am ded"
        await message.channel.send(msg)
    elif (
        message.content.startswith(",vote")
        or message.content.startswith(",hack")
        or message.content.startswith(",rig")
    ):
        await message.channel.send("Can't do that unfortunately, I'm not Russian")
    elif message.content.startswith(",tip") or message.content.startswith(",donate"):
        msg = "This bot took a while to make, and as a broke college student, I'd really appreciate a donation if you make any money off predictit...\n"
        msg += "    Bitcoin: \n    bc1qxmm7l2vhema687hrvle3yyp04h6svzy8tkk8sg\n"
        msg += "    PayPay, Venmo, etc: \n    PM @crazycrabman#2555\n"
        await message.channel.send(msg)
    elif message.content.startswith(",r all"):
        stats["commands"]["risk"] = stats["commands"].get("risk", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        print("Risk")
        await message.channel.send(embed=discord_api.risk_all())
    elif message.content.startswith(",r "):
        stats["commands"]["risk"] = stats["commands"].get("risk", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        argument = message.content.split(" ")
        shares = 850
        if len(argument) > 2:
            try:
                minimize = True
                shares = int(argument[-1])
                market = argument[1:-1]
            except ValueError:
                minimize = False
                market = argument[1:]
        else:
            minimize = False
            market = argument[1:]
        whole = ""
        for part in market:
            whole += part + " "
        market = whole[:-1]
        print("Risk")
        print(market, shares, message.author)
        await message.channel.send(
            embed=discord_api.risk_market(market, shares, minimize)
        )
    elif message.content.startswith(",topsecret"):
        await message.channel.send(embed=discord_api.risk_all())
    elif message.content.startswith(",b "):
        stats["commands"]["bins"] = stats["commands"].get("bins", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        market = message.content[3:]
        print("Bins")
        print(market, message.author)
        await message.channel.send(embed=discord_api.bins(market))
    elif (
        message.content.startswith(",v ")
        or message.content.startswith(",value")
        or message.content.startswith(",Value")
    ):
        stats["commands"]["rcp"] = stats["commands"].get("rcp", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        argument = message.content.split(" ")
        if len(argument) > 2:
            try:
                bin = int(argument[-1])
                market = argument[1:-1]
            except:
                market = argument[1:]
                bin = 1
        else:
            bin = 1
            market = argument[1:]
        whole = ""
        for part in market:
            whole += part + " "
        market = whole.strip()
        print("Value")
        print(market, bin, message.author)
        await message.channel.send(embed=discord_api.value_buy(market, bin))
    elif message.content.startswith(",. "):
        stats["commands"]["search_bins"] = stats["commands"].get("search_bins", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        keyword = message.content[3:]
        print("Similar")
        print(keyword, message.author)
        await message.channel.send(embed=discord_api.related_markets_bin(keyword))
    elif message.content.startswith(",- "):
        stats["commands"]["search_titles"] = (
            stats["commands"].get("search_titles", 0) + 1
        )
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,donate)"
            )
        keyword = message.content[3:]
        print("Similar")
        print(keyword, message.author)
        await message.channel.send(embed=discord_api.related_markets_title(keyword))
    elif message.content.startswith(",o "):
        stats["commands"]["orderbook"] = stats["commands"].get("orderbook", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        market = message.content[3:]
        print("Offers")
        print(market, message.author)
        await message.channel.send(embed=discord_api.orderbook(market))
    elif message.content.startswith(",stock") or message.content.startswith(",s "):
        stats["commands"]["stocks"] = stats["commands"].get("stocks", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 100 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        argument = message.content.split(" ")
        market = argument[1:]
        whole = ""
        for part in market:
            whole += part + " "
        market = whole.strip()
        try:
            data = yf.Ticker(market)
            await message.channel.send(
                market
                + " is currently trading at $"
                + str(data.info["regularMarketPrice"])
            )
        except:
            await message.channel.send(market + " not found")
    elif message.content.startswith(",i") or message.content.startswith(",implied"):
        await message.channel.send(embed=discord_api.divide_bins(3698, 3633))
    elif message.content.startswith(",stats"):
        msg = ""
        for user, num in stats["users"].items():
            msg += user.name + ": " + str(num) + "\n"
        embed = discord.Embed(title="user stats", description=msg, color=2206669)
        await message.channel.send(embed=embed)
        msg = ""
        for command, num in stats["commands"].items():
            msg += command + ": " + str(num) + "\n"
        embed = discord.Embed(title="command stats", description=msg, color=2206669)
        await message.channel.send(embed=embed)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print(list(client.guilds))
    print("------")


client.run(auths.discord_token)
