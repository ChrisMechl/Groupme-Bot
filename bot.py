import requests
import time

outFile = 'messages.csv'
chatID = 'testID.txt'
with open(chatID, 'r') as f:
    chatID = str(f.read())

key = '?token='
with open('key.txt', 'r') as f:
    key += f.read()

def findFirstMessage(paramDict):
    response = request(paramDict)
    firstID = response['messages'][-1]['id']
    paramDict['before_id'] = firstID
    paramDict['limit'] = 100
    firstMessage = {}
    while True:
        try:
            response = request(paramDict)
        except: break
        if not response:
            break
        firstID = response['messages'][-1]['id']
        paramDict['before_id'] = firstID
        message = response['messages'][-1]
    firstMessage['name'] = message['name']
    firstMessage['user_id'] = message['user_id']
    firstMessage['favorited_by'] = message['favorited_by']
    firstMessage['id'] = message['id']
    firstMessage['text'] = message['text'].replace(',', ' ')
    firstMessage['text'] = firstMessage['text'].replace('\n', ' ')
    firstMessage['created_at'] = message['created_at']
    for attachment in message['attachments']:
        if attachment['type'] == 'image':
            firstMessage['attachments'] = attachment['url']
            break
        else:
            firstMessage['attachments'] = None
    return firstMessage

def request(paramDict):
    URL = 'https://api.groupme.com/v3'
    try:
        return (requests.get(URL + '/groups/' + chatID + '/messages' + key, params=paramDict)).json()['response']
    except:
        return None

def parse(paramDict, IDtoName, done=False):
    response = request(paramDict)
    if not response or len(response['messages']) == 0:
        return (IDtoName, None, True)
    lastID = None
    messages = response['messages']
    for mess in messages:
        message = {}
        usrID = mess['sender_id']
        message['user_id'] = mess['sender_id']
        lastID = mess['id']
        message['name'] = mess['name'].replace(',', ' ')
        message['favorited_by'] = mess['favorited_by']
        message['text'] = mess['text']
        message['id'] = mess['id']
        message['created_at'] = mess['created_at']
        if len(mess['attachments']) is not 0:
            for attachment in mess['attachments']:
                if attachment['type'] == 'image':
                    message['attachments'] = attachment['url']
                    break
        else: message['attachments'] = None
        if usrID not in IDtoName:
            IDtoName[usrID] = mess['name'].replace(',', ' ')
        writeMessage(message, IDtoName)
    paramDict['after_id'] = lastID


    return (IDtoName, paramDict, done)

def writeMessage(message, IDtoName):
    favorited = ''
    for i, ID in enumerate(message['favorited_by']):
        if i == len(message['favorited_by']) - 1:
            try:
                favorited = favorited + IDtoName[ID]
            except:
                favorited = favorited + str(ID)
        else:
            try:
                favorited = favorited + IDtoName[ID] + ' | '
            except:
                favorited = favorited + str(ID) + ' | '
    try:
        name = message['name'].replace('\n', ' ')
    except:
        name = 'null'
    try:
        text = message['text'].replace(',', ' ')
        text = text.replace(':', ' ')
        text = text.replace(';', ' ')
        text = text.replace('\n', ' ')
        text = text.replace('"', '""')
    except:
        text = 'null'
    try:
        if message['attachments'] is not None:
            attachment = message['attachments']
        else:
            attachment = 'null'
    except:
        attachment = 'null'
    count = len(message['favorited_by'])
    if count != 0:
        constructedStr = str(message['id']) + ',' + str(message['user_id']) + ',' + name + ',' + text + ',' + attachment + ',' + favorited + ',' + str(len(message['favorited_by'])) + ',' + str(message['created_at']) + '\n'
    else:
        constructedStr = str(message['id']) + ',' + str(message['user_id']) + ',' + name + ',' + text + ',' + attachment + ',' + favorited + ',' + str(len(message['favorited_by'])) + ',' + str(message['created_at']) +  '\n'
    with open('messages.csv', 'a') as f:
        f.write(constructedStr)

def main():
    with open(outFile, 'w') as f:
        f.write('MessageID,UserID,Name,Message,Attachments,Favorites,Favorite Count,Created At\n')
    IDtoName = {}
    paramDict = {'limit' : 1}
    firstMessage = findFirstMessage(paramDict)
    writeMessage(firstMessage, IDtoName)
    paramDict['after_id'] = firstMessage['id']
    paramDict['limit'] = 100
    del paramDict['before_id']
    done = False
    while not done:
        IDtoName, paramDict, done = parse(paramDict, IDtoName)



if __name__ == '__main__':
    timeStart = time.time()
    main()
    timeEnd = time.time()
    print(timeStart - timeEnd)