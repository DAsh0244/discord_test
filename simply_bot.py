import discord
import asyncio
from code import interact
import re
import media_from_yt as myt
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


DISCORD_MAX_FILE_SIZE = 8*1024*1024  # 8MB
yt_url = re.compile(r'^(?:https?\:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.?be)\/watch\?v=(.+?)(?:&.*)?$')



client = discord.Client()
PREFIX = '$'
TOKEN = 'NDE1MzY5OTcyMDEzODU4ODI2.DW-_3g.N6ixlZI2o6LeGrJEpU2O81zjOYc'
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if msg.content.startswith(PREFIX):
        msg_txt = msg.content[len(PREFIX):]
        if msg_txt.startswith('hello'):
            # await client.send_message(msg.channel, content = (dir(msg)))
            await client.send_message(msg.channel, content="Hello! {}".format(msg.author))
        else:
            await client.send_message(msg.channel, content='Unknown command {}'.format(msg_txt))
    else:
        try:
            id = yt_url.match(msg.content).group(1)
        except AttributeError:
            id = None
        if id is not None:
            try:
                info,track_list = await loop.run_in_executor(executor, myt.get_info, id)
                if info is not None:
                    await client.send_message(msg.channel, content='now processing: {} '.format(info['title']))
                    outfile, tracklist = await loop.run_in_executor(executor, _call(myt.grab_file, url=id,info=info,track_list=track_list))
                    if tracklist:
                        # logger.info('slicing chapters from origin...')
                        out_dir = await loop.run_in_executor(executor,_call(myt.slice_chapters, outfile, track_list, quality='2', ext='mp3'))
                        print(out_dir)
                        for root,dir,outfiles in os.walk(out_dir):
                            for outfile in outfiles:
                                await client.send_file(msg.channel, os.path.join(root,outfile))
                    else:
                        await client.send_file(msg.channel, outfile)
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
    client.run(TOKEN)