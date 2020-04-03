import requests
import time

chatID = str(11120169) #mongwater
#chatID = str(35812688) #ma bitches
key = '?token='
with open('key.txt', 'r') as f:
    key += f.read()

def request(paramDict):
    URL = 'https://api.groupme.com/v3'
    try:
        return (requests.get(URL + '/groups/' + chatID + '/messages' + key, params=paramDict)).json()['response']
    except:
        return None
def parse(paramDict, messageList, IDtoName, done=False):
    response = request(paramDict)
    if not response:
        return (messageList, IDtoName, None, True)
    lastID = None
    for mess in response['messages']:
        message = {}
        usrID = mess['sender_id']
        lastID = mess['id']
        message['name'] = mess['name'].replace(',', ' ')
        message['favoritedBy'] = mess['favorited_by']
        message['text'] = mess['text']
        if len(mess['attachments']) is not 0:
            for attachment in mess['attachments']:
                if attachment['type'] == 'image':
                    message['attachments'] = attachment['url']
                    break
        else: message['attachments'] = None
        if usrID not in IDtoName:
            IDtoName[usrID] = mess['name'].replace(',', ' ')
        messageList.append(message)
    paramDict['before_id'] = lastID


    return (messageList, IDtoName, lastID, done)

def writeFile(messageList, IDtoName):
    with open('messages.csv', 'w') as f:
        f.write('Name,Message,Attachments,Favorites,Favorite Count\n')
        #filewriter = csv.writer(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #filewriter.writerow(['Name', 'Message', 'Attachments', 'Favorites'])

        messageList.reverse()
        for message in messageList:
            favorited = ''
            for i, ID in enumerate(message['favoritedBy']):
                if i == len(message['favoritedBy']) - 1:
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
                text = text.replace('\n', ' ')
            except:
                text = 'null'
            try:
                if message['attachments'] is not None:
                    attachment = message['attachments']
                else:
                    attachment = 'null'
            except:
                attachment = 'null'
            count = len(message['favoritedBy'])
            if count != 0:
                constructedStr = name + ',' + text + ',' + attachment + ',' + favorited + ',' + str(len(message['favoritedBy'])) + '\n'
            else:
                constructedStr = name + ',' + text + ',' + attachment + ',' + favorited + ',' + '\n'
            f.write(constructedStr)
            #filewriter.writerow([message['name'], message['text'], message['attachments'], favorited])



def main():
    messageList = []
    IDtoName = {}
    paramDict = {'limit' : 1}
    messageList, IDtoName, lastID, done = parse(paramDict, messageList, IDtoName)
    if not done:
        paramDict['limit'] = 100
        while not done:
            messageList, IDtoName, lastID, done = parse(paramDict, messageList, IDtoName)
    writeFile(messageList, IDtoName)


if __name__ == '__main__':
    timeStart = time.time()
    main()
    timeEnd = time.time()
    print(timeStart - timeEnd)