# -------------------------------------------- 
# Logixal DES - AI Powered Enterprise Search
# __author__ : Dnyaneshwar Dewadkar 
#            : 12:16 PM 14/02/20
#            : duckduckgo.py 
#  
# --------------------------------------------


# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
#
# See LICENSE for terms of usage, modification and redistribution.

import sys

# from urllib.request import Request
import requests

__version__ = 0.242


def query(query_str, useragent='python-duckduckgo ' + str(__version__), safesearch=True, html=False, meanings=True,
          **kwargs):

    print(" Inside query")
    safesearch = '0' if safesearch else '-1'
    html = '0' if html else '1'
    meanings = '1' if meanings else '1'
    params = {
        'q': query_str,
        'o': 'json',
        'kp': safesearch,
        'no_redirect': '1',
        'no_html': html,
        'd': meanings,
    }
    params.update(kwargs)
    str_q = "q=" + query_str + "&o=json&kp=" + safesearch + "&no_redirect=1&no_html=" + html + "&d=" + meanings
    url = requests.utils.requote_uri('http://api.duckduckgo.com/?' + str_q)
    # print(url)
    response = requests.request('GET', url, headers={'User-Agent': useragent}).json()
    # print(response)
    return Results(response)


class Results(object):

    def __init__(self, json):
        self.type = {'A': 'answer', 'D': 'disambiguation',
                     'C': 'category', 'N': 'name',
                     'E': 'exclusive', '': 'nothing'}.get(json.get('Type', ''), '')

        self.json = json
        self.api_version = None  # compat

        self.heading = json.get('Heading', '')

        self.results = [Result(elem) for elem in json.get('Results', [])]
        self.related = [Result(elem) for elem in
                        json.get('RelatedTopics', [])]

        self.abstract = Abstract(json)
        self.redirect = Redirect(json)
        self.definition = Definition(json)
        self.answer = Answer(json)

        self.image = Image({'Result': json.get('Image', '')})


class Abstract(object):

    def __init__(self, json):
        self.html = json.get('Abstract', '')
        self.text = json.get('AbstractText', '')
        self.url = json.get('AbstractURL', '')
        self.source = json.get('AbstractSource')


class Redirect(object):

    def __init__(self, json):
        self.url = json.get('Redirect', '')


class Result(object):

    def __init__(self, json):
        self.topics = json.get('Topics', [])
        if self.topics:
            self.topics = [Result(t) for t in self.topics]
            return
        self.html = json.get('Result')
        self.text = json.get('Text')
        self.url = json.get('FirstURL')

        icon_json = json.get('Icon')
        if icon_json is not None:
            self.icon = Image(icon_json)
        else:
            self.icon = None


class Image(object):

    def __init__(self, json):
        self.url = json.get('Result')
        self.height = json.get('Height', None)
        self.width = json.get('Width', None)


class Answer(object):

    def __init__(self, json):
        self.text = json.get('Answer')
        self.type = json.get('AnswerType', '')


class Definition(object):
    def __init__(self, json):
        self.text = json.get('Definition', '')
        self.url = json.get('DefinitionURL')
        self.source = json.get('DefinitionSource')


def get_zci(q, web_fallback=True, priority=['answer', 'abstract', 'related.0', 'definition'], urls=True, **kwargs):
    '''A helper method to get a single (and hopefully the best) ZCI result.
    priority=list can be used to set the order in which fields will be checked for answers.
    Use web_fallback=True to fall back to grabbing the first web result.
    passed to query. This method will fall back to 'Sorry, no results.'
    if it cannot find anything.'''

    ddg = query('\\' + q, **kwargs)
    response = ''

    for p in priority:
        ps = p.split('.')
        type = ps[0]
        index = int(ps[1]) if len(ps) > 1 else None

        result = getattr(ddg, type)
        if index is not None:
            if not hasattr(result, '__getitem__'): raise TypeError('%s field is not indexable' % type)
            result = result[index] if len(result) > index else None
        if not result: continue

        if result.text: response = result.text
        if result.text and hasattr(result, 'url') and urls:
            if result.url: response += ' (%s)' % result.url
        if response: break

    # if there still isn't anything, try to get the first web result
    if not response and web_fallback:
        if ddg.redirect.url:
            response = ddg.redirect.url

    # final fallback
    if not response:
        response = 'Sorry, no results.'

    return response


def wikisearch(query_text):
    try:
        # query_text = "what is Machine learning?"

        q = query(query_text)
        # keys = q.json.keys()
        # sorted(keys)
        # for key in keys:
        #     sys.stdout.write(key)
        #     if type(q.json[key]) in [str, int]:
        #         print(':', q.json[key])
        #     else:
        #         sys.stdout.write('\n')
        #         for i in q.json[key]: print('\t', i)

        response ={
            "status": "Success",
            "data": q.json
        }
    except Exception as exception:
        # default_responses = ['Looks like I am unable to find what you are looking for. Please contact my master',
        #                      'Hey to respond you back, I need to be feed more data.',
        #                      'You may be looking for something, I may not have it.',
        #                      '']
        response = {
            "status": "Failure",
            "Message": "Failed to process the query",
            "Error": exception,
            "data": {}
        }
    finally:
        return response

# else:
#     print('Usage: %s [query]' % sys.argv[0])

# if __name__ == '__main__':
# print("Hi")
# main()
