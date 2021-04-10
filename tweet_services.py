import tweepy, time

keys = []
with open("reference_files/keys.txt") as f:
    for line in f:
        keys.append(line)

auth = tweepy.OAuthHandler(keys[0], keys[1])
auth.set_access_token(keys[2], keys[3])
api = tweepy.API(auth, wait_on_rate_limit=True)

LAST_SEEN = "reference_files/last-seen.txt"

COMMANDS = ["start",
            "play",
            "quit",
            "help"]

def readLastSeen(FILE_NAME):
    fileRead = open(FILE_NAME, 'r')
    lastSeenId = int(fileRead.read().strip())
    fileRead.close()
    return lastSeenId

def updateLastSeen(FILE_NAME, lastSeenId):
    fileWrite = open(FILE_NAME, 'w')
    fileWrite.write(str(lastSeenId))
    fileWrite.close()

def getNewMentions():
    return api.mentions_timeline(readLastSeen(LAST_SEEN), tweet_mode='extended')

def batchDelete(api):
    for status in tweepy.Cursor(api.user_timeline).items():
        try:
            api.destroy_status(status.id)
            print("Deleted:", status.id)
        except Exception:
            import traceback
            traceback.print_exc()
            print("Failed to delete:", status.id)

def processTweet(tweet):
    """
    Takes tweets mentioning the bot and passes all relevant data into a dictionary
    :param tweet: a Tweet object
    :return: dictionary of all Tweet data
    """
    data = {'cmd': None,
            'player': None,
            'id': None,
            'flag': None}
    text = tweet.full_text.lower()
    parts = text.split()

    # if the tweet has more than 3 words then do not process
    if len(parts) <= 3 and parts[1] in COMMANDS:
        data['cmd'] = parts[1]
        data['player'] = "@" + tweet.user.screen_name
        data['id'] = tweet.id
        data['flag'] = None
        if len(parts) == 3:
            try:
                data['flag'] = int(parts[2])
            except ValueError:
                data['flag'] = parts[2]
        # updateLastSeen(LAST_SEEN, data['id'])
        return data
    return False


def processTweetBatch(batch):
    """
    Processes all tweets in batch
    :param batch: group of Tweet objects
    :return: list of all processed tweet data dictionaries
    """
    allData = []
    for tweet in batch:
        if processTweet(tweet):
            allData.append(processTweet(tweet))
    return allData

def replyMessage(msg, tweetID, player):
    try:
        time.sleep(3)
        msg = player + " " + msg
        return api.update_status(msg, tweetID)
    except tweepy.error.TweepError as e:
        print(e)

def replyBoardMessage(board, tweetID, player, message=None):
    try:
        time.sleep(3)
        if message:
            boardMsg = player + "\n" + str(board) + "\n\n" + message
        else:
            boardMsg = player + "\n" + str(board)
        return api.update_status(boardMsg, tweetID)
    except tweepy.error.TweepError as e:
        print(e)
