"""
py-netvend - A Python API for netvend written by @BardiHarborow and Syriven.

This module centers around the Agent class, which is split into three parts:
* AgentCore (signing and sending commands)
* AgentBasic (formatting commands and parsing the server responses)
* AgentExtended (additional convenience methods).

AgentCore should be the most stable. Each extension adds usability, but may be
less stable.

Agent is an alias for the current class we consider stable (AgentExtended, at
the moment).

Created by:
@Syriven (1MphZghyHmmrzJUk316iHvZ55UthfHXR34) and;
@BardiHarborow (1Bardi4eoUvJomBEtVoxPcP8VK26E3Ayxn)

Special Thanks to /u/minisat_maker on reddit for the orginal concept for netvend.
"""

import sys, thread, math

if sys.hexversion < 0x02000000 or sys.hexversion >= 0x03000000:
    raise RuntimeError("netvend requires Python 2.x.")

import json, pybitcointools
try:
    import urllib, urllib2
    urlopen = urllib2.urlopen
    urlencode = urllib.urlencode
except ImportError:
    import urllib.request
    urlopen = urllib.request.urlopen
    import urllib.parse
    urlencode = urllib.parse.urlencode

NETVEND_URL = "http://ec2-54-213-176-154.us-west-2.compute.amazonaws.com/command.php"
NETVEND_VERSION = "0_1"

def unit_pow(unit):
    if unit.lower().startswith("usat"):
        return 0
    elif unit.lower().startswith("msat"):
        return 3
    elif unit.lower().startswith("sat"):
        return 6
    elif unit.lower() == "ubtc" or unit.lower() == "ubit":
        return 8
    elif unit.lower() == "mbtc" or unit.lower() == "mbit":
        return 11
    elif unit.lower() == "btc":
        return 14
    else:
        raise ValueError("cannot recognize unit")

def convert_value(amount, from_unit, to_unit):
    from_pow = unit_pow(from_unit)
    to_pow = unit_pow(to_unit)

    uSats = amount * math.pow(10, from_pow)
    return uSats / math.pow(10, to_pow)

def format_value(uSats):
    if uSats > math.pow(10, 13):
        return (convert_value(uSats, 'usat', 'btc'), 'BTC')
    elif uSats > math.pow(10, 10):
        return (convert_value(uSats, 'usat', 'mbtc'), 'mBTC')
    elif uSats > math.pow(10, 7):
        return (convert_value(uSats, 'usat', 'ubtc'), 'uBTC')
    elif uSats > math.pow(10, 5):
        return (convert_value(uSats, 'usat', 'sat'), 'sat')
    elif uSats > math.pow(10, 2):
        return (convert_value(uSats, 'usat', 'msat'), 'mSat')
    else:
        return (convert_value(uSats, 'usat', 'usat'), 'uSat')

class NetvendResponseError(BaseException):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return str(self.response['error_code'])+": "+str(self.response['error_info'])


class AgentCore(object):
    '''Base class providing a skeleton framework. This should be stable.'''
    def __init__(self, private, url=NETVEND_URL, seed=False):
        if seed:
            self._private = pybitcointools.sha256(private)
        else:
            try:
                self._private = pybitcointools.b58check_to_hex(private)
            except AssertionError:
                raise RuntimeError("Invalid private key. Did you mean to set seed=True?")

        self.address = pybitcointools.pubkey_to_address(pybitcointools.privtopub(self._private))
        self.url = url
    
    def get_address(self):
        return self.address
    
    def sign_command(self, command):
        return pybitcointools.ecdsa_sign(command, self._private)

    def send_command(self, command, sig):
        return urlopen(self.url, urlencode({'address': self.get_address(), 'command' : command, 'signed' : sig, "version" : NETVEND_VERSION})).read()
        
    def sign_and_send_command(self, command):
        sig = self.sign_command(command)
        return self.send_command(command, sig)
    

class AgentBasic(AgentCore):
    '''Class providing increased functionality (functions for all command types and afunction to make server output nicer). This should be stable.'''
    def __init__(self, private, url=NETVEND_URL, seed=False):
        AgentCore.__init__(self, private, url, seed)
        self.max_query_fee = 3000

    def set_max_query_fee(self, fee):
        self.max_query_fee = fee

    def post_process(self, data):
        try:
            data = json.loads(data)
        except ValueError:
            raise ValueError("Can't parse server response. Server responded with:\n" + data)
        return_dict = {}
        return_dict['success'] = data[0]
        if not return_dict['success']:
            return_dict['error_code'] = data[1]
            return_dict['error_info'] = data[2]
            raise NetvendResponseError(return_dict)
        else:
            return_dict['history_id'] = data[1]
            return_dict['charged'] = data[2]
            raw_command_result = data[3]
            if isinstance(raw_command_result, int): # For Tips and Data
                command_result = raw_command_result
            else: # For Query
                command_result = {}
                command_result['success'] = raw_command_result[0]
                if command_result['success']:
                    command_result['num_rows'] = raw_command_result[1]
                    command_result['rows'] = raw_command_result[2]
                    command_result['field_types'] = raw_command_result[3]
                else:
                    fees = {'base': raw_command_result[1][0],
                            'time': raw_command_result[1][1],
                            'size': raw_command_result[1][2],
                            'total': raw_command_result[1][3]
                            }
                    command_result['fees'] = fees
            return_dict['command_result'] = command_result
        return return_dict

    def handle_command_asynch(self, command, callback):
        if not callable(callback):
            raise TypeError("can't use type " + type(callback) + " as a callback.")
        server_response = self.sign_and_send_command(command)
        callback(self.post_process(server_response))

    def handle_command(self, command, callback):
        if callback is None:
            return self.post_process(self.sign_and_send_command(command))
        else:
            thread.start_new_thread(self.handle_command_asynch, (command, callback))
        
    def post(self, data, callback=None):
        return self.handle_command(json.dumps(['p', data], separators=(',',':')), callback)

    def tip(self, address, amount, data_id, callback=None):
        if data_id == None:
            data_id = 0
        return self.handle_command(json.dumps(['t', address, amount, data_id], separators=(',',':')), callback)
    
    def query(self, sql, callback=None):
        return self.handle_command(json.dumps(['q', sql, self.max_query_fee], separators=(',',':')), callback)
    
    def withdraw(self, amount, callback=None):
        return self.handle_command(json.dumps(['w', amount], separators=(',',':')), callback)

class AgentExtended(AgentBasic):
    '''NetVendCore - Less stable functionality. Experimental, may change at any time.'''
    
    def fetch_balance(self):
        query = "SELECT balance FROM accounts WHERE address = '" + self.get_address() + "'"
        response = self.query(query)
        balance = int(response['command_result']['rows'][0][0])
        balance -= response['charged']
        return balance

Agent = AgentExtended
