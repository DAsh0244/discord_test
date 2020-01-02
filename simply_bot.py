import discord
import asyncio
from code import interact
import re
from media_from_yt import media_from_yt as myt
import zipfile
import os
import shutil
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor
from functools import partial as _call
import logging
import multiprocessing

myt.logger.setLevel(logging.DEBUG)
myt.ch.setLevel(logging.DEBUG)

CHANNEL = 415359063719936005
DISCORD_MAX_FILE_SIZE = 8*1024*1024  # 8MB
yt_url = re.compile(r'^(?:https?\:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.?be)\/watch\?v=(.+?)(?:&.*)?$')

client = discord.Client()
PREFIX = '$'
TOKEN = os.environ.get('DISCORD_API_TOKEN')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    try:
        CH = client.get_channel(CHANNEL)
        # up_msg = await client.send(CH, "Bot is Up!")
        # old_msgs = await client.logs_from(CH)
        # old_msgs = await client.logs_from(CH, before=up_msg)
        completed_transactions = []
        uncompleted_transactions = []

        async for msg in CH.history(limit=500):

            if msg.content.startswith(PREFIX) or msg.id in completed_transactions:
                continue
            if msg.author == client.user:
                if msg.attachments:
                    # print(msg)
                    completed_transactions.append(msg.id)
            else:
                uncompleted_transactions.append(msg)
        for uncompleted_transaction in uncompleted_transactions:
            try:
                id = yt_url.match(msg.content).group(1)
                try:
                    info,track_list = await loop.run_in_executor(executor, myt.get_info, id)
                    if info is not None:
                        await msg.channel.send(content='now processing: {} '.format(info['title']))
                        outfile, tracklist = await loop.run_in_executor(executor, _call(myt.grab_file, url=id,info=info,track_list=track_list))
                        if tracklist:
                            logger.info('slicing chapters from origin...')
                            out_dir = await loop.run_in_executor(executor,_call(myt.slice_chapters, outfile, track_list, quality='2', ext='mp3'))
                            print(out_dir)
                            for root,dir,outfiles in os.walk(out_dir):
                                for outfile in outfiles:
                                    await msg.channel.send(file=discord.File(os.path.join(root,outfile)))
                        else:
                            await msg.channel.send(file=discord.File(outfile))
                except Exception as e:
                    exec_info = sys.exc_info()
                    traceback.print_exception(*exec_info)
                    try:
                        print(outfile)
                    except:
                        pass
            except AttributeError:
                pass

    except Exception as e:
        exec_info = sys.exc_info()
        traceback.print_exception(*exec_info)
 #   finally:
        # client.logout()
        # client.close()
  #      raise Exception('Failed on startup')

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if msg.content.startswith(PREFIX):
        msg_txt = msg.content[len(PREFIX):]
        if msg_txt.startswith('hello'):
            # await msg.channel.send(content = (dir(msg)))
            await msg.channel.send(content="Hello! {}".format(msg.author))
        else:
            await msg.channel.send(content='Unknown command {}'.format(msg_txt))
    else:
        try:
            id = yt_url.match(msg.content).group(1)
        except AttributeError:
            id = None
        if id is not None:
            try:
                info,track_list = await loop.run_in_executor(executor, myt.get_info, id)
                if info is not None:
                    await msg.channel.send(content='now processing: {} '.format(info['title']))
                    outfile, tracklist = await loop.run_in_executor(executor, _call(myt.grab_file, url=id,info=info,track_list=track_list))
                    if tracklist:
                        # logger.info('slicing chapters from origin...')
                        out_dir = await loop.run_in_executor(executor,_call(myt.slice_chapters, outfile, track_list, quality='2', ext='mp3'))
                        print(out_dir)
                        for root,dir,outfiles in os.walk(out_dir):
                            for outfile in outfiles:
                                await msg.channel.send(file=discord.File(os.path.join(root,outfile)))
                    else:
                        await msg.channel.send(file=discord.File(outfile))
            except Exception as e:
                exec_info = sys.exc_info()
                traceback.print_exception(*exec_info)
                try:
                    print(outfile)
                except:
                    pass

# client.connect()
# client.login(TOKEN)
# client.start(TOKEN)
# interact(local=dict(globals(), **locals()))
if __name__ == '__main__':
    executor = ProcessPoolExecutor()
    loop  = asyncio.get_event_loop()
    try:
        client.run(TOKEN)
    # except KeyboardInterrupt:
      #   pass
    except Exception as e:
        exec_info = sys.exc_info()
        traceback.print_exception(*exec_info)
    finally:
        # client.logout()
        # client.close()
        loop.run_until_complete(client.close)
