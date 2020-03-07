import asyncio
import auths
import discord
import requests
import json
import yfinance as yf
from model import Model
from api import Discord
from api import PredictIt

pi_api = PredictIt(auths.username, auths.password)
discord_api = Discord(pi_api)
client = discord.Client()
stats = {'users': {}, 'commands': {}}
ca = Model('california', None, 0)
tx = Model('texas', None, 0)
al = Model('alabama', None, 0)
ar = Model('arkansas', None, 0)
co = Model('colorado', None, 0)
ma = Model('maine', None, 0)
mas = Model('massachusetts', None, 0)
mi = Model('minnesota', None, 0)
nc = Model('north-carolina', None, 0)
ok = Model('oklahoma', None, 0)
te = Model('tennessee', None, 0)
ut = Model('utah', None, 0)
va = Model('vermont', None, 0)
vi = Model('virginia', None, 0)


@client.event
async def on_message(message):
    if message.author == client.user:
        pass
    elif message.content.startswith(",Help") or message.content.startswith(",help") or message.content.startswith(",h"):
        stats['commands']['help'] = stats['commands'].get('help', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        title = "Here are the commands I can perform:\n"
        msg = ",h brings up this message.\n"
        msg += ",r figures out whether a market has negative risk or not. The keyword 'all' searches all the markets.\n"
        msg += ",b shows the prices for each bin in a market.\n"
        msg += ",v compares the cost of buying Yes and buying no on everything else.\n"
        msg += ",- gets all the markets that contain the input in the title.\n"
        msg += ",. gets all the markets that contain the input in the one of the bins.\n"
        msg += ",o gets the volume of the contracts in a specific market.\n"
        msg += ",rcp gets the current rcp averages for the nation or individual states.\n"
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
    elif message.content.startswith(",vote") or message.content.startswith(",hack") or message.content.startswith(
            ",rig"):
        await message.channel.send("Can't do that unfortunately, I'm not Russian")
    elif message.content.startswith(",tip") or message.content.startswith(",donate"):
        msg = "This bot took a while to make, and as a broke college student, I'd really appreciate a donation if you make any money off predictit...\n"
        msg += "    Bitcoin: \n    bc1qxmm7l2vhema687hrvle3yyp04h6svzy8tkk8sg\n"
        msg += "    PayPay, Venmo, etc: \n    PM @crazycrabman#2555\n"
        await message.channel.send(msg)
    elif message.content.startswith(",r all"):
        stats['commands']['risk'] = stats['commands'].get('risk', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        print("Risk")
        await message.channel.send(embed=discord_api.risk_all())
    elif message.content.startswith(",r "):
        stats['commands']['risk'] = stats['commands'].get('risk', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        argument = message.content.split(' ')
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
        await message.channel.send(embed=discord_api.risk_market(market, shares, minimize))
    elif message.content.startswith(",topsecret"):
        await message.channel.send(embed=discord_api.risk_all())
    elif message.content.startswith(",b "):
        stats['commands']['bins'] = stats['commands'].get('bins', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        market = message.content[3:]
        print("Bins")
        print(market, message.author)
        await message.channel.send(embed=discord_api.bins(market))
    elif message.content.startswith(",v ") or message.content.startswith(",value") or message.content.startswith(
            ",Value"):
        stats['commands']['rcp'] = stats['commands'].get('rcp', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        argument = message.content.split(' ')
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
        stats['commands']['search_bins'] = stats['commands'].get('search_bins', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        keyword = message.content[3:]
        print("Similar")
        print(keyword, message.author)
        await message.channel.send(embed=discord_api.related_markets_bin(keyword))
    elif message.content.startswith(",- "):
        stats['commands']['search_titles'] = stats['commands'].get('search_titles', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,donate)")
        keyword = message.content[3:]
        print("Similar")
        print(keyword, message.author)
        await message.channel.send(embed=discord_api.related_markets_title(keyword))
    elif message.content.startswith(",o "):
        stats['commands']['orderbook'] = stats['commands'].get('orderbook', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        market = message.content[3:]
        print("Offers")
        print(market, message.author)
        await message.channel.send(embed=discord_api.orderbook(market))
    elif message.content.startswith(",rcp") or message.content.startswith(",RCP"):
        stats['commands']['rcp'] = stats['commands'].get('rcp', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        argument = message.content.split(' ')
        keyword = argument[1:]
        whole = ""
        for part in keyword:
            whole += part + " "
        keyword = whole.strip()
        if keyword.lower() == 'iowa' or keyword.lower() == 'ia':
            title = "RCP average for Iowa"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6731_historical.js").text[12:][:-2]
        elif keyword.lower() == 'nv' or keyword.lower() == 'nevada':
            title = "RCP average for Nevada"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6866_historical.js").text[12:][:-2]
        elif keyword.lower() == 'nh' or keyword.lower() == 'new hampshire':
            title = "RCP average for New Hampshire"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6276_historical.js").text[12:][:-2]
        elif keyword.lower() == 'sc' or keyword.lower() == 'south carolina':
            title = "RCP average for South Carolina"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6824_historical.js").text[12:][:-2]
        elif keyword.lower() == 'national' or keyword.lower() == 'nation':
            title = "RCP average for the nation"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6730_historical.js").text[12:][:-2]
        elif keyword.lower() == 'california' or keyword.lower() == 'ca':
            title = "RCP average for California"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6879_historical.js").text[12:][:-2]
        elif keyword.lower() == 'texas' or keyword.lower() == 'tx':
            title = "RCP average for Texas"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6875_historical.js").text[12:][:-2]
        elif keyword.lower() == 'massachusetts' or keyword.lower() == 'ma':
            title = "RCP average for Massachusetts"
            averages = requests.get("https://www.realclearpolitics.com/epolls/json/6786_historical.js").text[12:][:-2]
        averages = json.loads(averages)
        max_len = 0
        for candidate in averages['poll']['rcp_avg'][0]['candidate']:
            if len(candidate['name']) > max_len and candidate['value']:
                max_len = len(candidate['name'])
        msg = "```Name" + '  ' + (' ' * (max_len - 4)) + "Average\n"
        for candidate in averages['poll']['rcp_avg'][0]['candidate']:
            if candidate['value']:
                msg += candidate['name'] + '  ' + (' ' * (max_len - len(candidate['name']))) + str(
                    candidate['value']) + '\n'
        msg += '```'
        print("RCP")
        print(keyword, message.author)
        embed = discord.Embed(title=title, description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",stock") or message.content.startswith(",s "):
        stats['commands']['stocks'] = stats['commands'].get('stocks', 0) + 1
        stats['users'][message.author] = stats['users'].get(message.author, 0) + 1
        if stats['users'][message.author] % 100 == 0:
            await message.channel.send("I see you've been using the bot quite a bit. Please consider donating some of your winnings! (,tip)")
        argument = message.content.split(' ')
        market = argument[1:]
        whole = ""
        for part in market:
            whole += part + " "
        market = whole.strip()
        try:
            data = yf.Ticker(market)
            await message.channel.send(market + " is currently trading at $" + str(data.info['regularMarketPrice']))
        except:
            await message.channel.send(market + " not found")
    elif message.content.startswith(",stats"):
        msg = ""
        for user, num in stats['users'].items():
            msg += user.name + ": " + str(num) + '\n'
        embed = discord.Embed(title="user stats", description=msg, color=2206669)
        await message.channel.send(embed=embed)
        msg = ""
        for command, num in stats['commands'].items():
            msg += command + ": " + str(num) + '\n'
        embed = discord.Embed(title="command stats", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",ca"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = ca.merged_totals()
        else:
            results = ca.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(ca.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="CA Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",tx"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = tx.merged_totals()
        else:
            results = tx.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(tx.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="TX Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",al"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = al.merged_totals()
        else:
            results = al.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(al.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="AL Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",ak"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = ar.merged_totals()
        else:
            results = ar.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(ar.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="AK Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",co"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = co.merged_totals()
        else:
            results = co.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(co.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="CO Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",me"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = ma.merged_totals()
        else:
            results = ma.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(ma.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="ME Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",ma"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = mas.merged_totals()
        else:
            results = mas.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(mas.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="MA Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",mn"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = mi.merged_totals()
        else:
            results = mi.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(mi.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="MN Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",nc"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = nc.merged_totals()
        else:
            results = nc.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(nc.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="NC Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",ok"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = ok.merged_totals()
        else:
            results = ok.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(ok.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="OK Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",tn"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = te.merged_totals()
        else:
            results = te.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(te.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="TN Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",ut"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = ut.merged_totals()
        else:
            results = ut.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(ut.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="UT Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",vt"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = va.merged_totals()
        else:
            results = va.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(va.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="VT Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",va"):
        print("Getting South Carolina Results")
        split = message.content.split(' ')
        argument = split[1:]
        whole = ""
        for part in argument:
            whole += part + " "
        argument = whole.strip()
        if not argument:
            results = vi.merged_totals()
        else:
            results = vi.best_county(argument)
        msg = '```\n'
        for key, value in sorted(results.items(), key=lambda x: -x[1]):
            msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(round(value/(results['Total']+0.000001)*100, 2)) + "%\n"
        msg += str(vi.get_best_reporting()) + '% Reporting'
        msg += '```\n'
        embed = discord.Embed(title="VA Results", description=msg, color=2206669)
        await message.channel.send(embed=embed)
    elif message.content.startswith(",cws") and str(message.author.id) == "324063771339259904":
        await message.channel.send("Wow it actually worked")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(list(client.guilds))
    print('------')


async def my_background_task():
    await client.wait_until_ready()
    print('starting')
    while client.is_ready():
        for message in discord_api.check_swings():
            await client.get_channel(668340965714690048).send(embed=message)
        await asyncio.sleep(15)


async def poll_check():
    await client.wait_until_ready()
    old1 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old2 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old3 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old4 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old5 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old6 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old7 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old8 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old9 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old10 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old11 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old12 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old13 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    old14 = {'Klobuchar': 1, 'Sanders': 0, 'Warren': 0, 'Yang': 0, 'Steyer': 0, 'Biden': 0, 'Buttigieg': 0,
            'Bloomberg': 0, 'Total': 0}
    while client.is_ready():
        print()
        print("checking results")
        results1 = ca.merged_totals()
        results2 = tx.merged_totals()
        results3 = al.merged_totals()
        results4 = ar.merged_totals()
        results5 = co.merged_totals()
        results6 = ma.merged_totals()
        results7 = mas.merged_totals()
        results8 = mi.merged_totals()
        results9 = nc.merged_totals()
        results10 = ok.merged_totals()
        results11 = te.merged_totals()
        results12 = ut.merged_totals()
        results13 = va.merged_totals()
        results14 = vi.merged_totals()
        if results1 != old1:
            old1 = results1
            print("new results")
            print(old1)
            msg = '```\n'
            for key, value in sorted(old1.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old1['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(ca.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="CA Results", description=msg, color=2206669)
            await client.get_channel(681077489271046149).send(embed=embed)
            print(old1)
        if results2 != old2:
            old2 = results2
            print("new results")
            print(old2)
            msg = '```\n'
            for key, value in sorted(old2.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old2['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(tx.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="TX Results", description=msg, color=2206669)
            await client.get_channel(681077680946413569).send(embed=embed)
            print(old2)
        if results3 != old3:
            old3 = results3
            print("new results")
            print(old3)
            msg = '```\n'
            for key, value in sorted(old3.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old3['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(al.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="AL Results", description=msg, color=2206669)
            await client.get_channel(681077897930342403).send(embed=embed)
            print(old3)
        if results4 != old4:
            old4 = results4
            print("new results")
            print(old4)
            msg = '```\n'
            for key, value in sorted(old4.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old4['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(ar.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="AR Results", description=msg, color=2206669)
            await client.get_channel(681078217146499092).send(embed=embed)
            print(old4)
        if results5 != old5:
            old5 = results5
            print("new results")
            print(old5)
            msg = '```\n'
            for key, value in sorted(old5.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old5['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(co.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="CO Results", description=msg, color=2206669)
            await client.get_channel(681078278844579851).send(embed=embed)
            print(old5)
        if results6 != old6:
            old6 = results6
            print("new results")
            print(old6)
            msg = '```\n'
            for key, value in sorted(old6.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old6['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(ma.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="MA Results", description=msg, color=2206669)
            await client.get_channel(681078315582488586).send(embed=embed)
            print(old6)
        if results7 != old7:
            old7 = results7
            print("new results")
            print(old7)
            msg = '```\n'
            for key, value in sorted(old7.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old7['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(mas.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="MAS Results", description=msg, color=2206669)
            await client.get_channel(681077646401994833).send(embed=embed)
            print(old7)
        if results8 != old8:
            old8 = results8
            print("new results")
            print(old8)
            msg = '```\n'
            for key, value in sorted(old8.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old8['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(mi.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="MI Results", description=msg, color=2206669)
            await client.get_channel(681078365616341044).send(embed=embed)
            print(old8)
        if results9 != old9:
            old9 = results9
            print("new results")
            print(old9)
            msg = '```\n'
            for key, value in sorted(old9.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old9['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(nc.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="NC Results", description=msg, color=2206669)
            await client.get_channel(681078421396389958).send(embed=embed)
            print(old9)
        if results10 != old10:
            old10 = results10
            print("new results")
            print(old10)
            msg = '```\n'
            for key, value in sorted(old10.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old10['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(ok.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="OK Results", description=msg, color=2206669)
            await client.get_channel(681078483094732842).send(embed=embed)
            print(old10)
        if results11 != old11:
            old11 = results11
            print("new results")
            print(old11)
            msg = '```\n'
            for key, value in sorted(old11.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old11['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(te.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="TE Results", description=msg, color=2206669)
            await client.get_channel(681078716599894049).send(embed=embed)
            print(old11)
        if results12 != old12:
            old12 = results12
            print("new results")
            print(old12)
            msg = '```\n'
            for key, value in sorted(old12.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old12['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(ut.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="UT Results", description=msg, color=2206669)
            await client.get_channel(681078772371554304).send(embed=embed)
            print(old12)
        if results13 != old13:
            old13 = results13
            print("new results")
            print(old13)
            msg = '```\n'
            for key, value in sorted(old13.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old13['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(va.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="VT Results", description=msg, color=2206669)
            await client.get_channel(681078808652283920).send(embed=embed)
            print(old13)
        if results14 != old14:
            old14 = results14
            print("new results")
            print(old14)
            msg = '```\n'
            for key, value in sorted(old14.items(), key=lambda x: -x[1]):
                msg += key + " " * (11 - len(key)) + str(value) + " " * (7 - len(str(value))) + str(
                    round(value / (old14['Total'] + 0.00000001) * 100, 2)) + "%\n"
            msg += str(vi.get_best_reporting()) + '% Reporting'
            msg += '```\n'
            embed = discord.Embed(title="VA Results", description=msg, color=2206669)
            await client.get_channel(681078854520930324).send(embed=embed)
            print(old14)
        await asyncio.sleep(5)


client.loop.create_task(my_background_task())
# client.loop.create_task(poll_check())
client.run(auths.discord_token)
