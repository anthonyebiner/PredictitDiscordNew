import asyncio
import unicodedata

import discord
import yfinance as yf

import auths
from api import Discord
from api import PredictIt
from votes import WisconsinRecount

pi_api = PredictIt()
discord_api = Discord(pi_api)
client = discord.Client()
stats = {"users": {}, "commands": {}}
nums = ["zero", "one","two","three","four","five","six","seven","eight","nine"]
emojis = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 10)]


@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    user = client.get_user(payload.user_id)
    emoji = payload.emoji.name
    try:
        message = await channel.fetch_message(payload.message_id)
    except AttributeError:
        return
    if user == client.user:
        pass
    elif message.author == client.user:
        title = message.embeds[0].title
        if "99% Bets's bets" in title:
            try:
                string = unicodedata.name(emoji[0]).split(" ")[1].lower()
                page = nums.index(string) - 1
                embed, pages = discord_api.list_bets(page, "99% Bets", False)
                await message.edit(embed=embed)
            except Exception as error:
                pass
        elif " as a bin" in title:
            try:
                string = unicodedata.name(emoji[0]).split(" ")[1].lower()
                page = nums.index(string) - 1
                embed, pages = discord_api.related_markets_bin(message.embeds[0].title.split('"')[1], page)
                await message.edit(embed=embed)
            except:
                pass
        elif " in the title" in title:
            try:
                string = unicodedata.name(emoji[0]).split(" ")[1].lower()
                page = nums.index(string) - 1
                embed, pages = discord_api.related_markets_title(message.embeds[0].title.split('"')[1], page)
                await message.edit(embed=embed)
            except:
                pass
        elif "Leaderboard" in title:
            try:
                string = unicodedata.name(emoji[0]).split(" ")[1].lower()
                page = nums.index(string) - 1
                embed, pages = discord_api.leaderboard(page)
                await message.edit(embed=embed)
            except Exception as error:
                pass
        elif "'s bets" in title:
            try:
                string = unicodedata.name(emoji[0]).split(" ")[1].lower()
                page = nums.index(string) - 1
                embed, pages = discord_api.list_bets(page, title.split("'")[0], True)
                await message.edit(embed=embed)
            except Exception as error:
                pass

        if unicodedata.name(emoji[0]) == "CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS":
            if "99% Bets's bets" in title:
                page = int(message.embeds[0].description.split("```")[1].split("\n")[0]) - 1
                embed, pages = discord_api.list_bets(page, "99% Bets", False)
                if embed.description != message.embeds[0].description:
                    await message.edit(embed=embed)
            elif " as a bin" in title:
                page = int(message.embeds[0].description.split(" ")[-3]) - 1
                embed, pages = discord_api.related_markets_bin(message.embeds[0].title.split('"')[1], page)
                if embed.description != message.embeds[0].description:
                    await message.edit(embed=embed)
            elif " in the title" in title:
                page = int(message.embeds[0].description.split(" ")[-3]) - 1
                embed, pages = discord_api.related_markets_title(message.embeds[0].title.split('"')[1], page)
                if embed.description != message.embeds[0].description:
                    await message.edit(embed=embed)
            elif "markets with negative risk" in title:
                hidden = message.embeds[0].description.split("```")[1].split("\n")[0]
                num = None if hidden == "None" else int(hidden)
                embed = discord_api.risk_all(num)
                if embed.description != message.embeds[0].description:
                    await message.edit(embed=embed)
            elif "Market risk for" in title:
                hidden = message.embeds[0].description.split("```")[1].split("\n")[0].split(".")
                num = None if hidden[1] == "None" else int(hidden[1])
                mini = True if hidden[2] == "True" else False
                embed = discord_api.risk_market(hidden[0], num, mini)
                if embed.description != message.embeds[0].description:
                    await message.edit(embed=embed)
            elif "Orderbook for " in title:
                hidden = message.embeds[0].description.split("```")[1].split("\n")[0]
                embed = discord_api.orderbook(hidden)
                if embed.description != message.embeds[0].description:
                    await message.edit(embed=embed)
            elif "Market bins for " in title:
                hidden = message.embeds[0].description.split("```")[1].split("\n")[0].replace(' ', '.')
                embed = discord_api.bins(hidden)
                if embed.description != message.embeds[0].description:
                    await message.edit(embed=embed)


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
        if stats["users"][message.author] % 35 == 0:
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
        msg += ",99 presents a list of bets we believe are almost certain to resolve true.\n"
        msg += ",stock or ,s gets the last traded price of the indicated ticker. \n"
        msg += "\nPredictIt Paper Trading\n"
        msg += ",buy buys a contract.\n"
        msg += ",sell sells a contract (can only do this once per contract).\n"
        msg += ",bets displays a list of the given user's bets.\n"
        msg += ",profit says how much the given user would have made if you maxed all of their bets when they were added.\n"
        msg += ",leaderboard presents a ranking of the most profitable traders.\n"
        msg += "\n"
        msg += "This bot took a while to make, and as a broke college student, I'd really appreciate a donation if like the bot or find it useful.\n"
        msg += "    Ethereum: 0x0B14678d91eBC9412c6F66d164e27f2866CD5906\n"
        msg += "    Bitcoin: bc1qxmm7l2vhema687hrvle3yyp04h6svzy8tkk8sg\n"
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
        msg += "    Ethereum: 0x0B14678d91eBC9412c6F66d164e27f2866CD5906\n"
        msg += "    Bitcoin: bc1qxmm7l2vhema687hrvle3yyp04h6svzy8tkk8sg\n"
        msg += "    PayPay, Venmo, etc: \n    PM @crazycrabman#2555\n"
        await message.channel.send(msg)
    elif message.content.startswith(",r all"):
        stats["commands"]["risk"] = stats["commands"].get("risk", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        print("Risk")
        m = await message.channel.send(embed=discord_api.risk_all())
        await m.add_reaction("\N{Clockwise Rightwards and Leftwards Open Circle Arrows}")
    elif message.content.startswith(",r "):
        stats["commands"]["risk"] = stats["commands"].get("risk", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
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
        m = await message.channel.send(
            embed=discord_api.risk_market(market, shares, minimize)
        )
        await m.add_reaction("\N{Clockwise Rightwards and Leftwards Open Circle Arrows}")
    elif message.content.startswith(",topsecret"):
        await message.channel.send(embed=discord_api.risk_all())
    elif message.content.startswith(",b "):
        stats["commands"]["bins"] = stats["commands"].get("bins", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        market = message.content[3:]
        print("Bins")
        print(market, message.author)
        m = await message.channel.send(embed=discord_api.bins(market))
        await m.add_reaction("\N{Clockwise Rightwards and Leftwards Open Circle Arrows}")
    elif (
        message.content.startswith(",v ")
        or message.content.startswith(",value")
        or message.content.startswith(",Value")
    ):
        stats["commands"]["rcp"] = stats["commands"].get("rcp", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
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
        if stats["users"][message.author] % 35 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        keyword = message.content[3:]
        print("Similar")
        print(keyword, message.author)
        embed, pages = discord_api.related_markets_bin(keyword, 0)
        m = await message.channel.send(embed=embed)
        for i in range(0, pages):
            await m.add_reaction(emojis[i])
        await m.add_reaction("\N{Clockwise Rightwards and Leftwards Open Circle Arrows}")
    elif message.content.startswith(",- "):
        stats["commands"]["search_titles"] = (
            stats["commands"].get("search_titles", 0) + 1
        )
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,donate)"
            )
        keyword = message.content[3:]
        print("Similar")
        print(keyword, message.author)
        embed, pages = discord_api.related_markets_title(keyword, 0)
        m = await message.channel.send(embed=embed)
        for i in range(0, pages):
            await m.add_reaction(emojis[i])
        await m.add_reaction("\N{Clockwise Rightwards and Leftwards Open Circle Arrows}")
    elif message.content.startswith(",o "):
        stats["commands"]["orderbook"] = stats["commands"].get("orderbook", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        market = message.content[3:]
        print("Offers")
        print(market, message.author)
        m = await message.channel.send(embed=discord_api.orderbook(market))
        await m.add_reaction("\N{Clockwise Rightwards and Leftwards Open Circle Arrows}")
    elif message.content.startswith(",stock") or message.content.startswith(",s "):
        stats["commands"]["stocks"] = stats["commands"].get("stocks", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
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
    elif message.content.startswith(",add"):
        authed = False
        try:
            if message.author.id == 324063771339259904:
                authed = True
            else:
                for role in message.author.roles:
                    if role.name == "moderators":
                        authed = True
        except:
            pass
        if not authed:
            embed = discord.Embed(title="Unauthorized", description="You are not authorized to perform this action", color=2206669)
            await message.channel.send(embed=embed)
            return
        argument = message.content.split(" ")
        try:
            market = int(argument[1])
            contract = int(argument[2])
            side = argument[3].lower()
            if side == "n" or side == "no":
                side = False
            else:
                side = True
            p = discord_api.buy(market, contract, side, "99% Bets")
            if p is not None:
                side = "YES" if p.side else "NO"
                embed = discord.Embed(title="Success", description=str(p.market) + "[" + str(p.contract) + " " + side + "]", color=2206669)
                await message.channel.send(embed=embed)
                return
        except:
            pass
        embed = discord.Embed(title="Failed", description="Input must be in the form 'MARKET BIN SIDE', where "
                                                          "MARKET is the id of the market, BIN is the bin number "
                                                          "of the contract, and SIDE is yes/no", color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",99"):
        stats["commands"]["99"] = stats["commands"].get("99", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        embed, pages = discord_api.list_bets(message.content.count('+'), "99% Bets", False)
        m = await message.channel.send(embed=embed)
        for i in range(0, pages):
            await m.add_reaction(emojis[i])
        await m.add_reaction("\N{Clockwise Rightwards and Leftwards Open Circle Arrows}")
    elif message.content.startswith(",profit99"):
        await message.channel.send(embed=discord_api.profit("99% Bets"))
    elif message.content.startswith(",project99"):
        await message.channel.send(embed=discord_api.project("99% Bets"))
    elif message.content.startswith(",buy"):
        argument = message.content.split(" ")
        try:
            market = int(argument[1])
            contract = int(argument[2])
            side = argument[3].lower()
            if side == "n" or side == "no":
                side = False
            else:
                side = True
            p = discord_api.buy(market, contract, side, message.author.name)
            if p == 0:
                embed = discord.Embed(title="Failed", description="You already bought this contract!", color=2206669)
                await message.channel.send(embed=embed)
                return
            if p is not None:
                side = "YES" if side else "NO"
                embed = discord.Embed(title="Success",
                                      description=str(p.market) + "[" + str(p.contract) + " " + side + "]",
                                      color=2206669)
                await message.channel.send(embed=embed)
                return
        except:
            pass
        embed = discord.Embed(title="Failed", description="Input must be in the form 'MARKET BIN SIDE', where "
                                                          "MARKET is the id of the market, BIN is the bin number "
                                                          "of the contract, and SIDE is yes/no", color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",sell"):
        argument = message.content.split(" ")
        try:
            market = int(argument[1])
            contract = int(argument[2])
            side = argument[3].lower()
            if side == "n" or side == "no":
                side = False
            else:
                side = True
            p = discord_api.sell(market, contract, side, message.author.name)
            if p is not None:
                embed = discord.Embed(title="Success",
                                      description="You made $" + str(p) + "!",
                                      color=2206669)
                await message.channel.send(embed=embed)
                return
        except Exception as error:
            print(error)
            pass
        embed = discord.Embed(title="Failed", description="Input must be in the form 'MARKET BIN SIDE', where "
                                                          "MARKET is the id of the market, BIN is the bin number "
                                                          "of the contract, and SIDE is yes/no", color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",bets"):
        argument = message.content.split(" ")
        if len(argument) == 1:
            user = message.author.name
        else:
            user = " ".join(argument[1:])
        embed, pages = discord_api.list_bets(message.content.count('+'), user, True)
        m = await message.channel.send(embed=embed)
        for i in range(0, pages):
            await m.add_reaction(emojis[i])
    elif message.content.startswith(",leaderboard"):
        embed, pages = discord_api.leaderboard(message.content.count('+'))
        m = await message.channel.send(embed=embed)
        for i in range(0, pages):
            await m.add_reaction(emojis[i])
    elif message.content.startswith(",profit"):
        await message.channel.send(embed=discord_api.profit(message.author.name))
    elif message.content.startswith(",remove"):
        authed = False
        try:
            if message.author.id == 324063771339259904:
                authed = True
            else:
                for role in message.author.roles:
                    if role.name == "moderators":
                        authed = True
        except:
            pass
        if not authed:
            embed = discord.Embed(title="Unauthorized", description="You are not authorized to perform this action", color=2206669)
            await message.channel.send(embed=embed)
            return
        argument = message.content.split(" ")
        market = int(argument[1])
        contract = int(argument[2])
        side = argument[3].lower()
        if side == "n" or side == "no":
            side = False
        else:
            side = True
        embed = discord_api.remove(" ".join(argument[4:]), market, contract, side)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",poly"):
        stats["commands"]["poly"] = stats["commands"].get("poly", 0) + 1
        stats["users"][message.author] = stats["users"].get(message.author, 0) + 1
        if stats["users"][message.author] % 35 == 0:
            await message.channel.send(
                "I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)"
            )
        argument = message.content.split(" ")
        embed = discord_api.poly_bins(" ".join(argument[1:]))
        await message.channel.send(embed=embed)
    elif message.content.startswith(",cat"):
        await message.channel.send(embed=discord_api.cat())
    elif message.content.startswith(",dog"):
        await message.channel.send(embed=discord_api.dog())
    elif message.content.startswith(",calc"):
        argument = message.content.split(" ")
        await message.channel.send(embed=discord_api.calc(" ".join(argument[1:])))


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print(list(client.guilds))
    print("------")


async def my_background_task():
    await client.wait_until_ready()
    biden_old, trump_old = -79, -20
    while client.is_ready():
        wisconsinRecount.reload_data()
        biden, trump = wisconsinRecount.count()
        if biden != biden_old or trump != trump_old:
            biden_old = biden
            trump_old = trump
            await client.get_channel(668340965714690048).send(embed=discord.Embed(title="Wisconsin Recount Vote Change", description="Biden " + str(biden) + "\nTrump " + str(trump) + "\nNet Biden " + str(biden-trump) + "\n<@!324063771339259904>"))
            await client.get_channel(717551703972511796).send(embed=discord.Embed(title="Wisconsin Recount Vote Change",
                                                                                  description="Biden " + str(
                                                                                      biden) + "\nTrump " + str(
                                                                                      trump) + "\nNet Biden " + str(
                                                                                      biden - trump)))
        await asyncio.sleep(60)

wisconsinRecount = WisconsinRecount()

client.loop.create_task(my_background_task())
client.run(auths.discord_token)
