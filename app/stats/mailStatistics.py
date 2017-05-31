from pattern.web import Mail, GMAIL, SUBJECT
import operator
import getpass
import re

def encode_utf8(string):
    # Returns the given string as a Python byte string (if possible).
    if isinstance(string, unicode):
        try:
            return string.encode("utf-8")
        except:
            return string
    return str(string)


def mostUsedWordsInFolder(mail, folder, isCaseSensitive, nbMails, nbWords):
    print(mail.folders.keys())

    if folder not in mail.folders:
        print("ERROR: Folder doesn't exist!")
        return

    print('Reading ' + str(mail.folders[folder].count) + ' emails from ' + folder)

    # Create word count dictionary. A dict where key=word, value=word count
    dictionary = {}

    # List of prefixes indicating it is a reply message
    replyPrefixes = ['RE:', 'Re:', 'RES:', 'Res:']

    # Create list of identifiers of reply lines (we call reply line
    # the line introducing the quoted text in a reply message)
    replyLineIdentifiers = []

    # List of regular expressions to be filtered from the results
    filterlist = [r"[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\.[a-zA-Z]+", r"[0-9]*\/[0-9][0-9]?\/[0-9]*", r"https?\:\/\/.*"]
    subj_filterlist = [r"[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9][a-zA-Z0-9\.\-\_]*\.[a-zA-Z]+", r"[0-9]*\/[0-9][0-9]?\/[0-9]*", r"https?\:\/\/.*", r"\[.+\]"]

    # Regular expression of word separators
    separators = r"[\s\.\,\;\:\!\?\(\)\<\>\"\'\*\\\/\=\+\~\_\[\]\{\}]+"

    # Number of emails to be analyzed
    n = min(mail.folders[folder].count, nbMails)

    for i in range(n):

        # Create list of words.
        words = []

        print('Reading mail ' + str(i+1) + ' of ' + str(n))

        # Read old messages first
        j = mail.folders[folder].count - i - 1
        message = mail.folders[folder].read(j, attachments=False, cached=False)

        print(message)

        #---- Email subject ----

        subject = message.subject

        # Check if it is a reply message. If so, do not count the subject
        # as it is a repetition of the first message's subject.
        isReply = False
        subjectPrefix = subject.split(None,1)
        if subjectPrefix != []:
            if subjectPrefix[0] in replyPrefixes:
                isReply = True
        if not isReply:
            subjectWords = subject.split()
            for word in subjectWords:
                words = splitAndAddWord(word, subj_filterlist, separators, words)

        #---- Email body ----

        if isReply:
            # Search for a reply line. Only count words before the first reply line.
            lines = message.body.splitlines()
            replyLineFound = False
            for line in lines:
                for s in replyLineIdentifiers:
                    if re.search(s['name'], line) and re.search(s['email'], line):
                        replyLineFound = True
                        break
                if replyLineFound:
                    break
                else:
                    bodyWords = line.split()
                    for word in bodyWords:
                        words = splitAndAddWord(word, filterlist, separators, words)
        else:
            bodyWords = message.body.split()
            for word in bodyWords:
                words = splitAndAddWord(word, filterlist, separators, words)

        # Count words and add them to the dictionary
        countWords(dictionary, words, isCaseSensitive)

        # Update the reply line identifiers by adding the author's name and email address
        replyLineIdentifiers = updateReplyLineIdentifiers(replyLineIdentifiers, message, isReply)


    words = []
    counts = []
    sortedDictionary = sorted(dictionary.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    nbw = 0
    for key, value in sortedDictionary:
        if nbw == nbWords:
            break
        words.append(encode_utf8(key))
        counts.append(value)
        nbw += 1
    return words, counts


def splitAndAddWord(word, filters, separators, wordlist):
    # If the word matches a filter, do not add it
    inFilter = False
    for regexp in filters:
        if re.search(regexp, word):
            inFilter = True
            break
    if not inFilter:
        # Split word and add the resulting words to the word list
        wordlist.extend(re.split(separators, word))
    return wordlist


def updateReplyLineIdentifiers(list, message, isReply):
    # Get author's name and email address
    authorIdentity = message.author
    pos = authorIdentity.find(' <')
    authorName = authorIdentity[0:pos]
    authorEmail = message.email_address

    # Update the list of identifiers for the next message
    if isReply:
        list.append({'name':authorName, 'email':authorEmail})
    else:
        list = [{'name':authorName, 'email':authorEmail}]
    return list


def countWords(dictionary, words, isCaseSensitive):
    
    for word in words:

        # Transform to lower case
        if not isCaseSensitive:
            word = word.lower()

        # Ignores words with 3 or less characters
        if len(word) > 3:
            if word in dictionary:
                dictionary[word] += 1
            else:
                dictionary[word] = 1
