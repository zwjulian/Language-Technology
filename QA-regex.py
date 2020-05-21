#!/usr/bin/env python3

import requests
import re
import fileinput


# returns a list with all IDs that matched with the keyword
def get_id(word, prop):
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action': 'wbsearchentities', 'language': 'en', 'format': 'json'}
    if prop:
        params['type'] = 'property'
    params['search'] = word.rstrip()
    json = requests.get(url, params).json()
    if not json['search']:
        print("Couldn't find any URI for: \'" + word + "\'")
        return 0
    else:
        return json['search']


# Finds the keywords in the lines using regex
def get_keywords(line):
    line = re.sub(r' ?\?', '', line)
    keyword1 = re.search(r'(?:.* of) +(?:the |a )?(.*)\n', line)
    keyword1string = ''.join(keyword1.groups())
    keyword2 = re.search('(?i)(?:what|who) (?:is|are|were|was)(?: the| a)? (.*) of (?:the |a )?' + keyword1string + '\n', line)
    keyword2string = ''.join(keyword2.groups())

    if re.search(" were|are ", line) and re.search("s$", keyword2string):
        keyword2string = re.sub("s$", "", keyword2string)

    return keyword2string, keyword1string


# generates a query and executes it, returns false if it didn't print an answer and true if it did.
def generate_and_execute_query(prop, entity):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    }
    url = 'https://query.wikidata.org/sparql'
    query = '''SELECT ?answerLabel WHERE {
      wd:''' + entity + ' wdt:' + prop + ''' ?answer.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}'''
    print(query)
    data = requests.get(url, headers=headers, params={'query': query, 'format': 'json'}).json()

    if not data['results']['bindings']:
        return False

    for item in data['results']['bindings']:
        for var in item:
            print(item[var]['value'])
    return True


# functions that returns 10 questions I know my program can answer
def my_questions():
    return ("What are the symptoms of the flu?",
            "Who is the inventor of the automobile?",
            "What are symptoms of COVID-19 ?",
            "who are the inventors of the telephone", # this one is difficult because 'inventors' has to be made singular
            "What was the country of citizenship of Marie Curie?",  # this one is difficult because of 2 'of's
            "What was the disability of Stephen Hawking ",
            "what was the goal of the Apollo space program",
            "What is the radius of the Sun?",  # this one is difficult because the first result of sun is sunday
            "Who is the CEO of AMD?",  # this ons is difficult because the first result of AMD is wrong
            "what are the effects of a tsunami?")


# This function gets an array of possible IDs and tries to get answers with them.
# It will keep trying new IDs until it gets an answer or until there are no more possible IDs.
def line_handler(line):
    prop, entity = get_keywords(line)
    propIDs = get_id(prop, True)
    entityIDs = get_id(entity, False)

    if propIDs == 0 or entityIDs == 0:
        return

    for propID in propIDs:
        for entityID in entityIDs:
            answer = generate_and_execute_query(propID['id'], entityID['id'])
            if answer:
                return
    print("No answer could be found")


def main():
    questions = my_questions()
    for line in questions:
        print(line)

    for line in fileinput.input():
        line_handler(line)


if __name__ == "__main__":
    main()
