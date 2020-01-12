#!/usr/bin/env python
# coding=utf-8
#"""
#calc.py - Phenny Calculator Module
#Copyright 2008, Sean B. Palmer, inamidst.com
#Licensed under the Eiffel Forum License 2.
#
#http://inamidst.com/phenny/
#"""

import re
import math
import web
from decimal import Decimal

r_result = re.compile(r'(?i)<A NAME=results>(.*?)</A>')
r_tag = re.compile(r'<\S+.*?>')
degree_sign = u'\N{DEGREE SIGN}'

subs = [
    (' in ', ' -> '), 
    (' over ', ' / '), 
    ('£', 'GBP '), 
    ('€', 'EUR '), 
    ('\$', 'USD '), 
    (r'\bKB\b', 'kilobytes'), 
    (r'\bMB\b', 'megabytes'), 
    (r'\bGB\b', 'kilobytes'), 
    ('kbps', '(kilobits / second)'), 
    ('mbps', '(megabits / second)')
]

integers_regex = re.compile(r'\b[\d\.]+\b')

def calc(expr, advanced=False): #Returns the result as a float, advanced=True will enable functionality from the math module, if someone tries to run direct python code such as sys.exit(), this function will simply return None and do nothing
   def safe_eval(expr, symbols={}):
       return eval(expr, dict(__builtins__=None), symbols)
   def whole_number_to_float(match):
       group = match.group()
       if group.find('.') == -1:
           return group + '.0'
       return group
   expr = expr.replace('^','**') # Python normally interprets '^' as a bitwise XOR operator while '**' is the exponent operator, this can be safely commented out if users are aware of this
   expr = integers_regex.sub(whole_number_to_float, expr)
   if advanced:
       return safe_eval(expr, vars(math))
   else:
       return safe_eval(expr)
       
       

def calculate(phenny, input): 
    """Calculate things."""
    if not input.group(2):
        return phenny.reply("Nothing to calculate.")
    q = input.group(2)
    q = q.replace('\xcf\x95', 'phi') # utf-8 U+03D5
    q = q.replace('\xcf\x80', 'pi') # utf-8 U+03C0
    q = q.replace('÷', '/')
    q = q.replace('τ', 'tau') # 2π

    try:
        answer = str(calc(input.group(2), advanced=True))
        phenny.say(answer)

    #Placeholder text for possible errors
    except SyntaxError: #Bad syntax
        phenny.say("Syntax error")
    except ZeroDivisionError: #Tried to divide by zero
        phenny.say("You cannot divide by zero")
    except OverflowError: #Calculation result is too large
        phenny.say("The answer is too large")

calculate.commands = ['c','calc','calculate']
calculate.example = '.c 5 + 3'

def ctof(phenny, input):
    """Converts Celsius to Fahrenheit"""
    try:
        decimal_match = re.match(r'.*?(?P<celsius>-?[\d.]+)', input.group(2))
        celsiusstr = decimal_match.group('celsius')
        celsius = float(celsiusstr)
    except:
        return phenny.say("Sorry I need a numeric Celsius temperature value.")
    fahrenheit = round(Decimal(celsius * 1.8 + 32), 1)
    phenny.say(celsiusstr + degree_sign + 'C is ' + str(fahrenheit) + degree_sign + 'F')
ctof.commands = ['ctof', 'celsiustofahrenheit']
ctof.example = '.ctof 5'

def ftoc(phenny, input):
    """Converts Fahrenheit to Celsius"""
    try:
        decimal_match = re.match(r'.*?(?P<celsius>-?[\d.]+)', input.group(2))
        fahrenheitstr = decimal_match.group('celsius')
        fahrenheit = float(fahrenheitstr)
    except:
        return phenny.say("Sorry I need a numeric Fahrenheit temperature value.")
    celsius = round(Decimal((fahrenheit - 32) / 1.8), 1)
    phenny.say(fahrenheitstr + degree_sign + 'F is ' + str(celsius) + degree_sign + 'C')
ftoc.commands = ['ftoc', 'fahrenheittocelsius']
ftoc.example = '.ftoc 5'

def ctok(phenny, input):
    """Converts Celsius to Kelvin"""
    try:
        decimal_match = re.match(r'.*?(?P<celsius>-?[\d.]+)', input.group(2))
        celsiusstr = decimal_match.group('celsius')
        celsius = float(celsiusstr)
    except:
        return phenny.say("Sorry I need a numeric Celsius temperature value.")
    kelvin = round(Decimal(celsius + 273.15), 2)
    phenny.say(celsiusstr + degree_sign + 'C is ' + str(kelvin) + 'K')
ctok.commands = ['ctok', 'celsiustokelvin']
ctok.example = '.ctok 5'

def ktoc(phenny, input):
    """Converts Kelvin to Celsius"""
    try:
        non_decimal = re.compile(r'[^\d.]+')
        kelvinstr = non_decimal.sub('', input.group(2))
        kelvin = float(kelvinstr)
    except:
        return phenny.say("Sorry I need a numeric Kelvin temperature value.")
    celsius = round(Decimal(kelvin - 273.15), 1)
    phenny.say(kelvinstr + 'K is ' + str(celsius) + degree_sign + 'C')
ktoc.commands = ['ktoc', 'kelvintocelsius']
ktoc.example = '.ktoc 5'

def ftok(phenny, input):
    """Converts Fahrenheit to Kelvin"""
    try:
        decimal_match = re.match(r'.*?(?P<celsius>-?[\d.]+)', input.group(2))
        fahrenheitstr = decimal_match.group('celsius')
        fahrenheit = float(fahrenheitstr)
    except:
        return phenny.say("Sorry I need a numeric Fahrenheit temperature value.")
    kelvin = round(Decimal(((fahrenheit - 32) / 1.8) + 273.15), 2)
    phenny.say(fahrenheitstr + degree_sign + 'F is ' + str(kelvin) + 'K')
ftok.commands = ['ftok', 'fahrenheittokelvin']
ftok.example = '.ftok 5'

def ktof(phenny, input):
    """Converts Kelvin to Fahrenheit"""
    try:
        non_decimal = re.compile(r'[^\d.]+')
        kelvinstr = non_decimal.sub('', input.group(2))
        kelvin = float(kelvinstr)
    except:
        return phenny.say("Sorry I need a numeric Kelvin temperature value.")
    celsius = (kelvin - 273.15)
    fahrenheit = round(Decimal(celsius * 1.8 + 32), 1)
    phenny.say(kelvinstr + 'K is ' + str(fahrenheit) + degree_sign + 'F')
ktof.commands = ['ktof', 'fahrenheittokelvin']
ktof.example = '.ktof 5'



if __name__ == '__main__': 
    print(__doc__.strip())
