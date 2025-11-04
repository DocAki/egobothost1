import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
from flask import Flask, request, jsonify
import threading
import asyncio
import json
from datetime import datetime, timedelta
import webserver
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)

STATS_FILE = 'player_stats.json'
PLAYTIME_FILE = 'playtime_data.json'


def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)


def load_playtime():
    if os.path.exists(PLAYTIME_FILE):
        with open(PLAYTIME_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_playtime(data):
    with open(PLAYTIME_FILE, 'w') as f:
        json.dump(data, f, indent=4)


player_stats = load_stats()
playtime_data = load_playtime()

POSITION_IMAGES = {
    'ST': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431061232382644484/5ea9230dc6b9416d52a21f09c24abb38.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431061804439699598/06a3b49e9319265be33f4246732682b3.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431063595042607185/i-think-that-shidou-is-underrated-v0-10hqugnt9wqa1.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431063672511398049/best-aura-out-of-these-4-v0-v2fexkcjrmic1.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431064648362360962/df2a0122d23ccb46821c50675c0691ad.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431065137858478114/33856633d4568386983def7d8e99910e.png'
    ],
    'LW': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431061298111840400/204d1f25c9405ae1f3b8b2b099d06dee.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431064013499797657/6eb4110cbfd5af2862fd0960271426cd.png'
    ],
    'RW': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431061455968534599/efa6f874a16bd559c2e45e35c1fe3bac.png'
    ],
    'CM': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431061591453073491/aaab534cda0bd21345648c53cee09e1c.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431065058380742667/3da0929009286e78288204f5f8e3facc.png'
    ],
    'CAM': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431062002918232194/latest.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431062138717470730/12770899b3d3b67e0927b9e445a076be.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431063930456899604/982410106fcdec874bbac5c629c71a4d.png'
    ],
    'CDM': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431061882151768124/searching-for-reo-mikage-fanart-artists-v0-ugqsi28pw70b1.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431063049367719936/ae5b497aab0614e60e4f1743c7cdb6b0.png'
    ],
    'LB': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431062862549356654/66db7ca8fa1af1e163604f296888fb24.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431063195036156036/5aeca6961030d8679413f2d1b12662c0.png'
    ],
    'CB': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431062741959053312/e243f0188b715e44b9bfc03f39ea0a8c.png'
    ],
    'RB': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431062236390228080/3e39ba3c92bc17b1655cc88c08d39620.png'
    ],
    'GK': [
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431065618861264936/360.png',
        'https://cdn.discordapp.com/attachments/1256270163997888512/1431065845160869939/Screenshot_2025-10-23_184430.png'
    ]
}

VALID_POSITIONS = ['ST', 'LW', 'RW', 'CM', 'CAM', 'CDM', 'LB', 'CB', 'RB', 'GK']

app = Flask('')


@app.route('/')
def home():
    return "Blue Lock Bot is running!"


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"🔍 Webhook received! Player count: {len(data)}")
        print(f"🔍 Raw data: {data}")

        timestamp = datetime.utcnow().isoformat()

        for player in data:
            user_id = str(player['user_id'])
            print(f"📝 Processing player: {player['username']} (ID: {user_id})")

            if user_id not in playtime_data:
                playtime_data[user_id] = {
                    'username': player['username'],
                    'display_name': player['display_name'],
                    'datapoints': [],
                    'total_time': 0
                }
                print(f"✨ New player added: {player['username']}")

            playtime_data[user_id]['username'] = player['username']
            playtime_data[user_id]['display_name'] = player['display_name']
            playtime_data[user_id]['datapoints'].append(timestamp)
            playtime_data[user_id]['total_time'] += 0.5

        save_playtime(playtime_data)
        print(f"✅ Playtime data saved! Total players tracked: {len(playtime_data)}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 400


def run_flask():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()


@bot.event
async def on_ready():
    print(f'✅ {bot.user} is now online!')
    print(f'📊 Loaded {len(playtime_data)} players from playtime data')
    keep_alive()


@bot.command(name='debug')
async def debug(ctx):
    """Debug command to check playtime data"""
    embed = discord.Embed(
        title="🔍 Debug Information",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Total Players Tracked",
        value=f"`{len(playtime_data)}` players",
        inline=False
    )

    if playtime_data:
        recent_players = list(playtime_data.items())[-5:]
        player_info = []

        for user_id, data in recent_players:
            datapoint_count = len(data['datapoints'])
            last_seen = "Never"

            if data['datapoints']:
                last_datapoint = datetime.fromisoformat(data['datapoints'][-1])
                now = datetime.utcnow()
                time_diff = now - last_datapoint

                if time_diff.total_seconds() < 60:
                    last_seen = "Active now"
                elif time_diff.total_seconds() < 3600:
                    last_seen = f"{int(time_diff.total_seconds() / 60)} min ago"
                else:
                    last_seen = f"{int(time_diff.total_seconds() / 3600)} hours ago"

            player_info.append(
                f"**{data['username']}** (ID: {user_id})\n"
                f"└ Datapoints: {datapoint_count} | Last seen: {last_seen}"
            )

        embed.add_field(
            name="Recent Players",
            value="\n\n".join(player_info),
            inline=False
        )
    else:
        embed.add_field(
            name="Status",
            value="❌ No playtime data found. Webhook may not be receiving data.",
            inline=False
        )

    await ctx.send(embed=embed)


@bot.command(name='activity')
async def activity(ctx):
    current_players = []
    now = datetime.utcnow()

    for user_id, data in playtime_data.items():
        if not data['datapoints']:
            continue

        last_datapoint = datetime.fromisoformat(data['datapoints'][-1])
        if now - last_datapoint < timedelta(minutes=1):
            current_players.append(data)

    if not current_players:
        await ctx.send("❌ No players are currently active in Blue Lock: Eleven")
        return

    embed = discord.Embed(
        title="🎮 Active Players - Blue Lock: Eleven",
        description=f"**{len(current_players)}** players currently online",
        color=random.randint(0, 0xFFFFFF)
    )

    for player in current_players[:25]:
        hours = int(player['total_time'] // 60)
        mins = int(player['total_time'] % 60)
        time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

        embed.add_field(
            name=f"{player['display_name']} (@{player['username']})",
            value=f"Total Playtime: `{time_str}`",
            inline=False
        )

    await ctx.send(embed=embed)


@bot.command(name='playtime')
async def playtime(ctx, timeframe: str = "all"):
    if timeframe.lower() not in ['daily', 'weekly', 'all']:
        await ctx.send("**📊 Usage:** `.playtime [daily/weekly/all]`")
        return

    now = datetime.utcnow()
    player_times = []

    for user_id, data in playtime_data.items():
        total_time = 0

        for datapoint_str in data['datapoints']:
            datapoint = datetime.fromisoformat(datapoint_str)

            if timeframe.lower() == 'daily' and now - datapoint > timedelta(days=1):
                continue
            elif timeframe.lower() == 'weekly' and now - datapoint > timedelta(weeks=1):
                continue

            total_time += 0.5

        if total_time > 0:
            player_times.append({
                'display_name': data['display_name'],
                'username': data['username'],
                'time': total_time
            })

    if not player_times:
        await ctx.send(f"❌ No playtime data available for {timeframe}")
        return

    player_times.sort(key=lambda x: x['time'], reverse=True)

    timeframe_text = {
        'daily': 'Today',
        'weekly': 'This Week',
        'all': 'All Time'
    }

    embed = discord.Embed(
        title=f"⏱️ Playtime Leaderboard - {timeframe_text[timeframe.lower()]}",
        description=f"Top players by playtime",
        color=random.randint(0, 0xFFFFFF)
    )

    for i, player in enumerate(player_times[:25], 1):
        hours = int(player['time'] // 60)
        mins = int(player['time'] % 60)
        time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

        embed.add_field(
            name=f"#{i} {player['display_name']} (@{player['username']})",
            value=f"⏱️ `{time_str}`",
            inline=False
        )

    await ctx.send(embed=embed)


@bot.command(name='putstats')
@commands.has_permissions(administrator=True)
async def putstats(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    messages_to_delete = [ctx.message]

    try:
        q1 = await ctx.send("**📝 Please mention the player (@user):**")
        messages_to_delete.append(q1)
        user_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(user_msg)

        if not user_msg.mentions:
            error_msg = await ctx.send("❌ Please mention a valid user!")
            messages_to_delete.append(error_msg)
            await asyncio.sleep(3)
            await ctx.channel.delete_messages(messages_to_delete)
            return

        user = user_msg.mentions[0]
        user_id = str(user.id)
        display_name = user.display_name

        q2 = await ctx.send(
            f"**⚽ Please enter {display_name}'s position:**\n`ST, LW, RW, CM, CAM, CDM, LB, CB, RB, GK`")
        messages_to_delete.append(q2)
        position_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(position_msg)
        position = position_msg.content.upper()

        if position not in VALID_POSITIONS:
            error_msg = await ctx.send(f"❌ Invalid position! Please use one of: {', '.join(VALID_POSITIONS)}")
            messages_to_delete.append(error_msg)
            await asyncio.sleep(3)
            await ctx.channel.delete_messages(messages_to_delete)
            return

        q3 = await ctx.send("**⚽ Goals scored:**")
        messages_to_delete.append(q3)
        goals_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(goals_msg)
        goals = int(goals_msg.content)

        q4 = await ctx.send("**❌ Goals missed:**")
        messages_to_delete.append(q4)
        goals_missed_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(goals_missed_msg)
        goals_missed = int(goals_missed_msg.content)

        q5 = await ctx.send("**🎯 Assists:**")
        messages_to_delete.append(q5)
        assists_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(assists_msg)
        assists = int(assists_msg.content)

        q6 = await ctx.send("**✅ Passes completed:**")
        messages_to_delete.append(q6)
        passes_complete_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(passes_complete_msg)
        passes_complete = int(passes_complete_msg.content)

        q7 = await ctx.send("**❌ Passes missed/intercepted:**")
        messages_to_delete.append(q7)
        passes_missed_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(passes_missed_msg)
        passes_missed = int(passes_missed_msg.content)

        q8 = await ctx.send("**🛡️ Tackles completed:**")
        messages_to_delete.append(q8)
        tackles_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(tackles_msg)
        tackles = int(tackles_msg.content)

        q9 = await ctx.send("**❌ Tackles missed:**")
        messages_to_delete.append(q9)
        tackles_missed_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(tackles_missed_msg)
        tackles_missed = int(tackles_missed_msg.content)

        q10 = await ctx.send("**🧤 Saves:**")
        messages_to_delete.append(q10)
        saves_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(saves_msg)
        saves = int(saves_msg.content)

        q11 = await ctx.send("**❌ Saves missed:**")
        messages_to_delete.append(q11)
        saves_missed_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(saves_missed_msg)
        saves_missed = int(saves_missed_msg.content)

        q12 = await ctx.send("**🔄 Turnovers:**")
        messages_to_delete.append(q12)
        turnovers_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(turnovers_msg)
        turnovers = int(turnovers_msg.content)

        if user_id not in player_stats:
            player_stats[user_id] = {
                'display_name': display_name,
                'position': position,
                'goals': 0,
                'goals_missed': 0,
                'assists': 0,
                'passes_complete': 0,
                'passes_missed': 0,
                'tackles': 0,
                'tackles_missed': 0,
                'saves': 0,
                'saves_missed': 0,
                'turnovers': 0
            }

        player_stats[user_id]['display_name'] = display_name
        player_stats[user_id]['position'] = position
        player_stats[user_id]['goals'] += goals
        player_stats[user_id]['goals_missed'] += goals_missed
        player_stats[user_id]['assists'] += assists
        player_stats[user_id]['passes_complete'] += passes_complete
        player_stats[user_id]['passes_missed'] += passes_missed
        player_stats[user_id]['tackles'] += tackles
        player_stats[user_id]['tackles_missed'] += tackles_missed
        player_stats[user_id]['saves'] += saves
        player_stats[user_id]['saves_missed'] += saves_missed
        player_stats[user_id]['turnovers'] += turnovers

        save_stats(player_stats)

        total = player_stats[user_id]

        goal_efficiency = (total['goals'] / (total['goals'] + total['goals_missed']) * 100) if (total['goals'] + total[
            'goals_missed']) > 0 else 0
        pass_efficiency = (total['passes_complete'] / (total['passes_complete'] + total['passes_missed']) * 100) if (
                                                                                                                                total[
                                                                                                                                    'passes_complete'] +
                                                                                                                                total[
                                                                                                                                    'passes_missed']) > 0 else 0
        tackle_efficiency = (total['tackles'] / (total['tackles'] + total['tackles_missed']) * 100) if (total[
                                                                                                            'tackles'] +
                                                                                                        total[
                                                                                                            'tackles_missed']) > 0 else 0
        save_efficiency = (total['saves'] / (total['saves'] + total['saves_missed']) * 100) if (total['saves'] + total[
            'saves_missed']) > 0 else 0

        embed_color = random.randint(0, 0xFFFFFF)
        position_image = random.choice(POSITION_IMAGES[position])

        embed = discord.Embed(
            title=f"⚽ All-Time Stats - {display_name}",
            description=f"**Position:** {position}",
            color=embed_color
        )

        stats_table = f"""
**Goals** | **Assists** | **Passes Complete** | **Tackles** | **Saves** | **Turnovers**
`{total['goals']}` | `{total['assists']}` | `{total['passes_complete']}` | `{total['tackles']}` | `{total['saves']}` | `{total['turnovers']}`

**Goals Missed** | **Passes Missed** | **Missed Tackles** | **Saves Missed**
`{total['goals_missed']}` | `{total['passes_missed']}` | `{total['tackles_missed']}` | `{total['saves_missed']}`
        """

        embed.add_field(name="📊 Performance Stats", value=stats_table, inline=False)

        efficiency_table = f"""
**Goal Efficiency:** `{goal_efficiency:.1f}%`
**Pass Efficiency:** `{pass_efficiency:.1f}%`
**Tackle Efficiency:** `{tackle_efficiency:.1f}%`
**Save Efficiency:** `{save_efficiency:.1f}%`
        """

        embed.add_field(name="📈 Efficiency Ratings", value=efficiency_table, inline=False)
        embed.set_thumbnail(url=position_image)
        embed.set_footer(text=f"Stats recorded by {ctx.author.name}")

        await ctx.channel.delete_messages(messages_to_delete)
        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
        timeout_msg = await ctx.send("❌ Command timed out. Please try again.")
        messages_to_delete.append(timeout_msg)
        await asyncio.sleep(3)
        await ctx.channel.delete_messages(messages_to_delete)
    except ValueError:
        error_msg = await ctx.send("❌ Invalid input! Please enter numbers only for stats.")
        messages_to_delete.append(error_msg)
        await asyncio.sleep(3)
        await ctx.channel.delete_messages(messages_to_delete)
    except Exception as e:
        error_msg = await ctx.send(f"❌ An error occurred: {str(e)}")
        messages_to_delete.append(error_msg)
        await asyncio.sleep(3)
        await ctx.channel.delete_messages(messages_to_delete)


@bot.command(name='editstat')
@commands.has_permissions(administrator=True)
async def editstat(ctx, stat_name: str = None, user: discord.User = None, value: str = None):
    if not stat_name or not user or not value:
        await ctx.send(
            "**📊 Usage:** `.editstat <stat_name> @user <value>`\n**Stats:** goals, goals_missed, assists, passes_complete, passes_missed, tackles, tackles_missed, saves, saves_missed, turnovers, position")
        return

    user_id = str(user.id)
    stat_name = stat_name.lower()

    valid_stats = ['goals', 'goals_missed', 'assists', 'passes_complete', 'passes_missed', 'tackles',
                   'tackles_missed', 'saves', 'saves_missed', 'turnovers', 'position']

    if stat_name not in valid_stats:
        await ctx.send(f"❌ Invalid stat! Choose from: {', '.join(valid_stats)}")
        return

    if user_id not in player_stats:
        await ctx.send(f"❌ No stats found for **{user.display_name}**")
        return

    try:
        if stat_name == 'position':
            new_value = value.upper()
            if new_value not in VALID_POSITIONS:
                await ctx.send(f"❌ Invalid position! Choose from: {', '.join(VALID_POSITIONS)}")
                return
        else:
            new_value = int(value)

        player_stats[user_id][stat_name] = new_value
        save_stats(player_stats)

        await ctx.send(
            f"✅ Successfully updated **{stat_name}** to `{new_value}` for **{player_stats[user_id]['display_name']}**")

    except ValueError:
        await ctx.send("❌ Invalid value! Please enter a valid number.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")


@bot.command(name='resetallstats')
@commands.has_permissions(administrator=True)
async def resetallstats(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        confirm_msg = await ctx.send(
            "⚠️ **WARNING:** This will delete ALL player stats permanently!\nType `CONFIRM` to proceed or `CANCEL` to abort.")
        response = await bot.wait_for('message', check=check, timeout=30.0)

        if response.content.upper() == 'CONFIRM':
            global player_stats
            total_players = len(player_stats)
            player_stats = {}
            save_stats(player_stats)
            await ctx.send(f"✅ Successfully reset stats for **{total_players}** players!")
        else:
            await ctx.send("❌ Reset cancelled.")

    except asyncio.TimeoutError:
        await ctx.send("❌ Reset cancelled due to timeout.")


@editstat.error
async def editstat_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to use this command!")


@resetallstats.error
async def resetallstats_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to use this command!")


@putstats.error
async def putstats_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to use this command!")


@bot.command(name='viewstats')
async def viewstats(ctx, user: discord.User = None):
    if user is None:
        await ctx.send("**📊 Usage:** `.viewstats @user`")
        return

    user_id = str(user.id)

    if user_id not in player_stats:
        await ctx.send(f"❌ No stats found for player: **{user.display_name}**")
        return

    total = player_stats[user_id]
    position = total['position']
    display_name = total['display_name']

    goal_efficiency = (total['goals'] / (total['goals'] + total['goals_missed']) * 100) if (total['goals'] + total[
        'goals_missed']) > 0 else 0
    pass_efficiency = (total['passes_complete'] / (total['passes_complete'] + total['passes_missed']) * 100) if (total[
                                                                                                                     'passes_complete'] +
                                                                                                                 total[
                                                                                                                     'passes_missed']) > 0 else 0
    tackle_efficiency = (total['tackles'] / (total['tackles'] + total['tackles_missed']) * 100) if (total['tackles'] +
                                                                                                    total[
                                                                                                        'tackles_missed']) > 0 else 0
    save_efficiency = (total['saves'] / (total['saves'] + total['saves_missed']) * 100) if (total['saves'] + total[
        'saves_missed']) > 0 else 0

    embed_color = random.randint(0, 0xFFFFFF)
    position_image = random.choice(POSITION_IMAGES[position])

    embed = discord.Embed(
        title=f"⚽ All-Time Stats - {display_name}",
        description=f"**Position:** {position}",
        color=embed_color
    )

    stats_table = f"""
**Goals** | **Assists** | **Passes Complete** | **Tackles** | **Saves** | **Turnovers**
`{total['goals']}` | `{total['assists']}` | `{total['passes_complete']}` | `{total['tackles']}` | `{total['saves']}` | `{total['turnovers']}`

**Goals Missed** | **Passes Missed** | **Missed Tackles** | **Saves Missed**
`{total['goals_missed']}` | `{total['passes_missed']}` | `{total['tackles_missed']}` | `{total['saves_missed']}`
    """

    embed.add_field(name="📊 Performance Stats", value=stats_table, inline=False)

    efficiency_table = f"""
**Goal Efficiency:** `{goal_efficiency:.1f}%`
**Pass Efficiency:** `{pass_efficiency:.1f}%`
**Tackle Efficiency:** `{tackle_efficiency:.1f}%`
**Save Efficiency:** `{save_efficiency:.1f}%`
    """

    embed.add_field(name="📈 Efficiency Ratings", value=efficiency_table, inline=False)
    embed.set_thumbnail(url=position_image)

    await ctx.send(embed=embed)

webserver.keep_alive()

bot.run(TOKEN)
