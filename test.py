import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from time import time
from textwrap import wrap

env_path = Path.cwd() / '.env'
load_dotenv(env_path, override=True)

def getVk(lastCall):
    """
    This function gets recent posts from VK. Recent posts are 
    those posts which were published after last check.
    
    lastCall argument is an int timestamp value grabbed from redis variable
    called 'last_request_time'.
    """

    vkUrl = 'https://api.vk.com/method/'
    userGetMethod = 'users.get'
    wallGetMethod = 'wall.get'
    screenName = os.getenv('SCREEN_NAME')

    vkOptions = {
        'client_id' : os.getenv('CLIENT_ID'),
        'access_token' : os.getenv('ACCESS_TOKEN'),
        'v' : os.getenv('V'),
    }

    userData = requests.post(f'{vkUrl}{userGetMethod}?user_ids={screenName}', data = vkOptions).json()
    id = userData['response'][0]['id']

    r = requests.post(f'{vkUrl}{wallGetMethod}?owner_id={id}&count=20', data = vkOptions)

    r = list(
        filter(
            lambda x: x['date'] > lastCall,
            r.json()['response']['items']
            )
        )
    r.reverse()
    
    return r

def sendTg(posts):
    bot_token = os.getenv('BOT_TOKEN')
    sendMessageMethod = 'sendMessage'
    tgUrl = 'https://api.telegram.org/bot'
    chatId = os.getenv('CHAT_ID')

    tgPostMaxSize = 4096
    tgResponse = list()

    for post in posts:
        text = post.get('text', '')
        if post.get('copy_history'):
            text += post['copy_history'][0].get('text', '')
        if len(text) != 0:
            partition = wrap(text,  tgPostMaxSize)

            for part in partition:
                tgResponse.append(
                    str(post.get('id')) + 
                    '\n' +
                    requests.post(
                        f'{tgUrl}{bot_token}/{sendMessageMethod}?chat_id={chatId}&text={part}'
                        ).text
                    )
        else:
            tgResponse.append(
                str(post.get('id')) +
                '\n' +
                'No contents sent to tg'
            )
    return tgResponse
    
