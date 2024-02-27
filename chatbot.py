from pprint import pprint
import random
import nltk

# store = set of knowledge. contains the triples of person,fact,value. Fact is knowledge about them and have a value of that fact
knowledge = { ("person1", "name", "T"), \
              ("person1", "town", "T"),
              ("person1", "street", "T") }

active = True

acceptedVerbs = ["buy","order","purchase"]
endWords = ["bye","goodbye"]

# finds proper noun in the reply and returns it
# return -1 = unsupported operation
def processReplyUnknowns(reply):
    listOfWords = nltk.word_tokenize(reply) # split our reply into tokens which are similar to words

    # find nouns
    taggedListOfWords = nltk.pos_tag(listOfWords)
    for taggedPair in taggedListOfWords:
        if taggedPair[1] == "NNP" or taggedPair[1] == "NN":
            return taggedPair[0]

def processReplyKnowns(reply):
    listOfWords = nltk.word_tokenize(reply)

    taggedListOfWords = nltk.pos_tag(listOfWords)

    verbs = []

    for taggedPair in taggedListOfWords:
        if taggedPair[1] == "VB":
            verbs.append(taggedPair[0])

    if len(verbs) == 0:
        return "no reply"
    
    for verb in verbs:
        if verb in acceptedVerbs:
            return "wants to buy"
    return "no reply"


def endProgram():
    print(knowledge)
    active = False

while active:
    # unknown values in the knoweldge base
    unknowns = { (person,fact,value) for (person,fact,value) \
                 in knowledge if value=="?" }
    print("UNKNOWN:")
    pprint(unknowns)
    print("KNOWN:")
    pprint(knowledge - unknowns)

    # asking questions to fill in gaps in knowledge
    if unknowns: #is non-empty
        
        currentQuery = random.choice(tuple(unknowns))

        if currentQuery[1] == "wants to buy":
            question = "What do you want to buy ?"

        else:
            question = "What is your " + currentQuery[1] + "?"# asking a question about the fact
        
        reply = input(question)

        formatedReply = processReplyUnknowns(reply)

        unknowns.remove(currentQuery)
        knowledge.remove(currentQuery)
        
        knowledge.add((currentQuery[0],currentQuery[1],formatedReply))

    else:
        question = "How can I help you? "
        helpRequest = input(question)

        if(helpRequest in endWords):
            endProgram()
            break

        helpRequestProcessed = processReplyKnowns(helpRequest)

        if helpRequestProcessed == "no reply":
            print("I cannot help you with that. Can I help you to buy something?")
        elif helpRequestProcessed == "wants to buy":
            print("I can help with that!")
            knowledge.add(("person1","wants to buy","?"))

    print()

