#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web
import json

class Grab(web.urllib.request.URLopener):
    def __init__(self, *args):
        self.version = 'Mozilla/5.0 (CompuBot)'
        web.urllib.request.URLopener.__init__(self, *args)
        self.addheader('Referer', 'https://github.com/sbp/phenny')
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return web.urllib.addinfourl(fp, [headers, errcode], "http:" + url)

def google_ajax(query): 
    """Search using AjaxSearch, and return its JSON."""
    if isinstance(query, str): 
        query = query.encode('utf-8')
    uri = 'http://ajax.googleapis.com/ajax/services/search/web'
    args = '?v=1.0&safe=off&q=' + web.quote(query)
    handler = web.urllib.request._urlopener
    web.urllib.request._urlopener = Grab()
    bytes = web.get(uri + args)
    web.urllib.request._urlopener = handler
    return web.json(bytes)

def google_search(query): 
    results = google_ajax(query)
    try: return results['responseData']['results'][0]['unescapedUrl']
    except IndexError: return None
    except TypeError: 
        print(results)
        return False

def google_count(query): 
    results = google_ajax(query)
    if 'responseData' not in results: return '0'
    if 'cursor' not in results['responseData']: return '0'
    if 'estimatedResultCount' not in results['responseData']['cursor']: 
        return '0'
    return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n): 
    """Format a number with beautiful commas."""
    parts = list(str(n))
    for i in range((len(parts) - 3), 0, -3):
        parts.insert(i, ',')
    return ''.join(parts)

def g(phenny, input): 
    """Queries Google for the specified input."""
    query = input.group(2)
    if not query: 
        return phenny.reply('.g what?')
    uri = google_search(query)
    if uri: 
        phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    elif uri is False: phenny.reply("Problem getting data from Google.")
    else: phenny.reply("No results found for '%s'." % query)
g.commands = ['g']
g.priority = 'high'
g.example = '.g swhack'

def gc(phenny, input): 
    """Returns the number of Google results for the specified input."""
    query = input.group(2)
    if not query: 
        return phenny.reply('.gc what?')
    num = formatnumber(google_count(query))
    phenny.say(query + ': ' + num)
gc.commands = ['gc']
gc.priority = 'high'
gc.example = '.gc extrapolate'

r_query = re.compile(
    r'\+?"[^"\\]*(?:\\.[^"\\]*)*"|\[[^]\\]*(?:\\.[^]\\]*)*\]|\S+'
)

def gcs(phenny, input): 
    if not input.group(2):
        return phenny.reply("Nothing to compare.")
    queries = r_query.findall(input.group(2))
    if len(queries) > 6: 
        return phenny.reply('Sorry, can only compare up to six things.')

    results = []
    for i, query in enumerate(queries): 
        query = query.strip('[]')
        n = int((formatnumber(google_count(query)) or '0').replace(',', ''))
        results.append((n, query))
        if i >= 2: __import__('time').sleep(0.25)
        if i >= 4: __import__('time').sleep(0.25)

    results = [(term, n) for (n, term) in reversed(sorted(results))]
    reply = ', '.join('%s (%s)' % (t, formatnumber(n)) for (t, n) in results)
    phenny.say(reply)
gcs.commands = ['gcs', 'comp']

r_bing = re.compile(r'<h3><a href="([^"]+)"')

def bing_search(query, lang='en-GB'): 
    query = web.quote(query)
    base = 'http://www.bing.com/search?mkt=%s&q=' % lang
    bytes = web.get(base + query)
    m = r_bing.search(bytes)
    if m: return m.group(1)

def bing(phenny, input): 
    """Queries Bing for the specified input."""
    query = input.group(2)
    if query.startswith(':'): 
        lang, query = query.split(' ', 1)
        lang = lang[1:]
    else: lang = 'en-GB'
    if not query:
        return phenny.reply('.bing what?')

    uri = bing_search(query, lang)
    if uri: 
        phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.reply("No results found for '%s'." % query)
bing.commands = ['bing']
bing.example = '.bing swhack'

r_duck = re.compile(r'nofollow" class="[^"]+" href="(http.*?)">')

def duck_search(query): 
    query = query.replace('!', '')
    query = web.quote(query)
    uri = 'http://duckduckgo.com/html/?q=%s&kl=uk-en' % query
    rec_bytes = web.get(uri)
    m = r_duck.search(rec_bytes)
    if m: return web.decode(m.group(1))

def duck(phenny, input): 
    """Queries Duck Duck Go for the specified input."""
    query = input.group(2)
    if not query: return phenny.reply('.ddg what?')

    uri = duck_search(query)
    if uri: 
        phenny.reply(uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.reply("No results found for '%s'." % query)
duck.commands = ['ddg', 'duck']
duck.example = '.ddg swhack'



def wikipedia_search(query): 
    query = query.replace('!', '')
    query = web.quote(query)
    uri = 'https://en.wikipedia.org/w/api.php?action=query&list=search&continue=&srsearch=%s&format=json' % query
    rec_bytes = web.get(uri)
    jsonstring = json.loads(rec_bytes)
    wihits = jsonstring['query']['searchinfo']['totalhits']
    if wihits > 0:
        wititle = jsonstring['query']['search'][0]['title']
        wiwords = str(jsonstring['query']['search'][0]['wordcount'])
        wisearch = wititle.replace('!', '')
        wisearch = web.quote(wisearch)
        base_url = "https://en.wikipedia.org/wiki/"+wisearch
        return (wititle + " - " + wiwords + " words " + base_url)

def wikipedia(phenny, input): 
    """Queries Wikipedia for the specified input."""
    query = input.group(2)
    if not query: return phenny.reply('.wi what?')

    uri = wikipedia_search(query)
    if uri: 
        phenny.say("Here's what I got, " + input.nick + ": " + uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.say("Sorry " + input.nick + ", I couldn't find anything for '%s'." % query)
wikipedia.commands = ['wi', 'wikipedia']
wikipedia.example = '.wi swhack'

def weather_search(query, phenny): 
    if phenny.config.wunderground_api_key:
        query = query.replace('!', '')
        query = query.replace(' ', '_')
        query = web.quote(query)
        uri = 'http://api.wunderground.com/api/' + phenny.config.wunderground_api_key + '/conditions/q/' + query + '.json'
        rec_bytes = web.get(uri)
        jsonstring = json.loads(rec_bytes)
        werror = 0
        try:
            werrorexist = jsonstring['response']['error']['type']
            werror = 1
        except:
            werror = 0
            
        if werror is 1:
            werrortype = jsonstring['response']['error']['type']
            werrordesc = jsonstring['response']['error']['description']
            werrorfull = 'Error Code: ' + werrortype + ' - ' + werrordesc
            return werrorfull
        else:
            try:
                wcity = jsonstring['current_observation']['display_location']['full']
                wwinddir = str(jsonstring['current_observation']['wind_dir'])
                wwindspd = str(jsonstring['current_observation']['wind_mph'])
                wwindgust = str(jsonstring['current_observation']['wind_gust_mph'])
                wtemp = jsonstring['current_observation']['temperature_string']
                wfeels = jsonstring['current_observation']['feelslike_string']
                wuv = str(jsonstring['current_observation']['UV'])
                wcondition = jsonstring['current_observation']['weather']
                wurl = 'http://www.wunderground.com/?apiref=5284b9a94c2a6666'
                
                return ('In ' + wcity + ' it is currently ' + wcondition + ', the temperature is ' + wtemp + ' and it feels like ' + wfeels + '. The wind speed is ' + wwindspd + ' MPH ' + wwinddir + ' with gusts of up to ' + wwindgust + " MPH. The UV level is " + wuv + ". Weather from " + wurl)
            except KeyError:
                return None
    else:
        return 'Sorry but you need to set your wunderground_api_key in the config file.'

def weather(phenny, input): 
    """Queries Wunderground for the weather."""
    query = input.group(2)
    if not query: return phenny.reply('.w what?')

    uri = weather_search(query, phenny)
    if uri: 
        if uri.startswith('Error Code'):
            phenny.say("Sorry, " + input.nick +", I got an error. Here's the error i got, " + uri)
        else:
            phenny.say("Here's what I got, " + input.nick + ": " + uri)
            if not hasattr(phenny.bot, 'last_seen_uri'):
                phenny.bot.last_seen_uri = {}
            phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.say("Sorry " + input.nick + ', try something more specific than "' + query + '"')
weather.commands = ['w', 'weather']
weather.example = '.w San Francisco, CA'

def forecast_search(query, phenny): 
    if phenny.config.wunderground_api_key:
        query = query.replace('!', '')
        query = query.replace(' ', '_')
        query = web.quote(query)
        uri = 'http://api.wunderground.com/api/' + phenny.config.wunderground_api_key + '/conditions/forecast/q/' + query + '.json'
        rec_bytes = web.get(uri)
        jsonstring = json.loads(rec_bytes)
        wferror = 0
        try:
            wferrorexist = jsonstring['response']['error']['type']
            wferror = 1
        except:
            wferror = 0
            
        if wferror is 1:
            wferrortype = jsonstring['response']['error']['type']
            wferrordesc = jsonstring['response']['error']['description']
            wferrorfull = 'Error Code: ' + wferrortype + ' - ' + wferrordesc
            return wferrorfull
        else:
            try:
                wfcity = jsonstring['current_observation']['display_location']['full']
                wfdate1 = jsonstring['forecast']['simpleforecast']['forecastday'][0]['date']['weekday']
                wfdate2 = jsonstring['forecast']['simpleforecast']['forecastday'][1]['date']['weekday']
                wfdate3 = jsonstring['forecast']['simpleforecast']['forecastday'][2]['date']['weekday']
                wfdate4 = jsonstring['forecast']['simpleforecast']['forecastday'][3]['date']['weekday']
                wfcond1 = jsonstring['forecast']['simpleforecast']['forecastday'][0]['conditions']
                wfcond2 = jsonstring['forecast']['simpleforecast']['forecastday'][1]['conditions']
                wfcond3 = jsonstring['forecast']['simpleforecast']['forecastday'][2]['conditions']
                wfcond4 = jsonstring['forecast']['simpleforecast']['forecastday'][3]['conditions']
                wfhigh1f = str(jsonstring['forecast']['simpleforecast']['forecastday'][0]['high']['fahrenheit'])
                wfhigh2f = str(jsonstring['forecast']['simpleforecast']['forecastday'][1]['high']['fahrenheit'])
                wfhigh3f = str(jsonstring['forecast']['simpleforecast']['forecastday'][2]['high']['fahrenheit'])
                wfhigh4f = str(jsonstring['forecast']['simpleforecast']['forecastday'][3]['high']['fahrenheit'])
                wfhigh1c = str(jsonstring['forecast']['simpleforecast']['forecastday'][0]['high']['celsius'])
                wfhigh2c = str(jsonstring['forecast']['simpleforecast']['forecastday'][1]['high']['celsius'])
                wfhigh3c = str(jsonstring['forecast']['simpleforecast']['forecastday'][2]['high']['celsius'])
                wfhigh4c = str(jsonstring['forecast']['simpleforecast']['forecastday'][3]['high']['celsius'])
                wflow1f = str(jsonstring['forecast']['simpleforecast']['forecastday'][0]['low']['fahrenheit'])
                wflow2f = str(jsonstring['forecast']['simpleforecast']['forecastday'][1]['low']['fahrenheit'])
                wflow3f = str(jsonstring['forecast']['simpleforecast']['forecastday'][2]['low']['fahrenheit'])
                wflow4f = str(jsonstring['forecast']['simpleforecast']['forecastday'][3]['low']['fahrenheit'])
                wflow1c = str(jsonstring['forecast']['simpleforecast']['forecastday'][0]['low']['celsius'])
                wflow2c = str(jsonstring['forecast']['simpleforecast']['forecastday'][1]['low']['celsius'])
                wflow3c = str(jsonstring['forecast']['simpleforecast']['forecastday'][2]['low']['celsius'])
                wflow4c = str(jsonstring['forecast']['simpleforecast']['forecastday'][3]['low']['celsius'])
                
                degree_sign= u'\N{DEGREE SIGN}'
                wfurl = 'http://www.wunderground.com/?apiref=5284b9a94c2a6666'
                
                return ('The forecast for ' + wfdate1 + ' in ' + wfcity + ' is ' + wfcond1 + ' with a high of ' + wfhigh1f + degree_sign + 'F (' + wfhigh1c + degree_sign + 'C) and a low of ' + wflow1f + degree_sign + 'F (' + wflow1c + degree_sign + 'C). On ' + wfdate2 + ' it will be ' + wfcond2 + ' with a high of ' + wfhigh2f + degree_sign + 'F (' + wfhigh2c + degree_sign + 'C) and a low of ' + wflow2f + degree_sign + 'F (' + wflow2c + degree_sign + 'C). On ' + wfdate3 + ' it will be ' + wfcond3 + ' with a high of ' + wfhigh3f + degree_sign + 'F (' + wfhigh3c + degree_sign + 'C) and a low of ' + wflow3f + degree_sign + 'F (' + wflow3c + degree_sign + 'C). On ' + wfdate4 + ' it will be ' + wfcond4 + ' with a high of ' + wfhigh4f + degree_sign + 'F (' + wfhigh4c + degree_sign + 'C) and a low of ' + wflow4f + degree_sign + 'F (' + wflow4c + degree_sign + 'C).')
            except KeyError:
                return None
    else:
        return 'Sorry but you need to set your wunderground_api_key in the config file.'

def forecast(phenny, input): 
    """Queries Wunderground for the weather forecast."""
    query = input.group(2)
    if not query: return phenny.reply('.w what?')

    uri = forecast_search(query, phenny)
    if uri: 
        if uri.startswith('Error Code'):
            phenny.say("Sorry, " + input.nick +", I got an error. Here's the error i got, " + uri)
        else:
            phenny.say("Here's what I got, " + input.nick + ": " + uri)
            if not hasattr(phenny.bot, 'last_seen_uri'):
                phenny.bot.last_seen_uri = {}
            phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.say("Sorry " + input.nick + ', try something more specific than "' + query + '"')
forecast.commands = ['wf', 'forecast']
forecast.example = '.wf San Francisco, CA'

def search(phenny, input): 
    """Searches Duck Duck Go, Google, and Bing all at once."""
    if not input.group(2): 
        return phenny.reply('.search for what?')
    query = input.group(2)
    gu = google_search(query) or '-'
    bu = bing_search(query) or '-'
    du = duck_search(query) or '-'

    if (gu == bu) and (bu == du): 
        result = '%s (g, b, d)' % gu
    elif (gu == bu): 
        result = '%s (g, b), %s (d)' % (gu, du)
    elif (bu == du): 
        result = '%s (b, d), %s (g)' % (bu, gu)
    elif (gu == du): 
        result = '%s (g, d), %s (b)' % (gu, bu)
    else: 
        if len(gu) > 250: gu = '(extremely long link)'
        if len(bu) > 150: bu = '(extremely long link)'
        if len(du) > 150: du = '(extremely long link)'
        result = '%s (g), %s (b), %s (d)' % (gu, bu, du)

    phenny.reply(result)
search.commands = ['search']
search.example = '.search swhack'

def suggest(phenny, input): 
    if not input.group(2):
        return phenny.reply("No query term.")
    query = input.group(2)
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = web.get(uri + web.quote(query).replace('+', '%2B'))
    if answer: 
        phenny.say(answer)
    else: phenny.reply('Sorry, no result.')
suggest.commands = ['suggest']

if __name__ == '__main__': 
    print(__doc__.strip())
