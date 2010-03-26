#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

try:
    import memcache
    HAS_MEMCACHE = True
except ImportError:
    HAS_MEMCACHE = False
try:
    import cPickle as pickle
except:
    import pickle
from datetime import timedelta
import time
from threading import Lock

def exp_to_epoch(exp):
    if hasattr(exp,'timetuple'):
        return int(time.mktime(exp.timetuple()))
    if isinstance(exp, timedelta):
        exp = exp.days*86400 + exp.seconds
    return int(time+exp)

class GnrSharedData_dict(object):
    
    def __init__(self, site):
        self.storage = {}
        self.storage_lock = Lock()
        self.site = site
        self.cas_id = 0
        
    def _get_next_cas_id(self):
        self.cas_id +=1
        return self.cas_id
    next_cas_id = property(_get_next_cas_id)
        
    def set(self, key, value, expiry=0, cas_id=None):
        if expiry:
            expiry = exp_to_epoch(expiry)
        pickled_value = pickle.dumps(value)
        if cas_id is None:
            self.storage[key] = (pickled_value, expiry, self.next_cas_id)
            return True
        else:
            self.storage_lock.acquire()
            previous_cas_id = self.storage.get(key, (None,None,None))[2]
            if previous_cas_id!=cas_id:
                result = False
            else:
                self.storage[key] = (pickled_value, expiry, self.next_cas_id)
                result = True
            self.storage_lock.release()
            return result
            
    def gets(self, key):
        return self._get(key)
        
    def get(self, key):
        return self._get(key)[0]
    
    def _get(self, key):
        pickled_value, expiry, cas_id = self.storage[key]
        if time.time()> expiry:
            return None, None
        return pickle.loads(pickled_value), cas_id
    
    def delete(self, key, time=0):
        if key in self.storage:
            del self.storage[key]
    
    def incr(self, key, delta=1):
        if key in self.storage:
            if not type(self.storage[key])==int:
                self.storage[key]=0
            self.storage[key] += delta
            return self.storage[key]

    def decr(self, key, delta=1):
        if key in self.storage:
            if not type(self.storage[key])==int:
                self.storage[key]=0
            else:
                self.storage[key] -= delta
                if self.storage[key] < 0:
                    self.storage[key]=0
            return self.storage[key]
            
    def add(self, key, value, expiry = 0):
        if not key in self.storage:
            self.set(key, value, expiry = expiry)
            return value
            
    def replace (self, key, value, expiry = 0):
        if key in self.storage:
            self.set(key, value, expiry = expiry)
            return value
    
class GnrSharedData_memcache(object):

    def __init__(self,site, memcache_config=None):
        self.site = site
        self._namespace = site.site_name
        server_list = ['%(host)s:%(port)s'%attr for attr in memcache_config.digest('#a')]
        self.storage = memcache.Client(server_list, debug=memcache_config.parentNode.attr.get('debug',False))
        
    def key(self, key):
        return '%s_%s'%(self._namespace, key.encode('utf8'))
        
    def get(self, key):
        return self.storage.get(self.key(key))
        
    def gets(self, key):
        result = self.storage.gets(self.key(key))
        cas_id = self.storage.cas_ids.get(self.key(key))
        return result, cas_id

    def set(self, key, value, expiry=0, cas_id=None):
        if not cas_id:
            self.storage.set(self.key(key), value, time=exp_to_epoch(expiry))
        else:
            self.storage.cas_ids[self.key(key)]=cas_id
            self.storage.cas(self.key(key), value, time=exp_to_epoch(expiry))
    
    def add(self, key, value, expiry = 0):
        status = self.storage.add(key, value, time=exp_to_epoch(expiry))
        if status:
            return value
    
    def replace (self, key, value, expiry = 0):
        status = self.storage.replace(key, value, time=exp_to_epoch(expiry))
        if status:
            return value
    
    def delete(self, key, value):
        self.storage.delete(self.key(key))
        
    def incr(self, key, delta=1):
        return self.storage.incr(key, delta=delta)
        
    def decr(self, key, delta=1):
        return self.storage.decr(key, delta=delta)

class Client(object):

    def set_servers(self, servers):
        """
        Set the pool of servers used by this client.

        @param servers: an array of servers.
        Servers can be passed in two forms:
            1. Strings of the form C{"host:port"}, which implies a default weight of 1.
            2. Tuples of the form C{("host:port", weight)}, where C{weight} is
            an integer weight value.
        """
        pass

    def get_stats(self):
        '''Get statistics from each of the servers.

        @return: A list of tuples ( server_identifier, stats_dictionary ).
            The dictionary contains a number of name/value pairs specifying
            the name of the status field and the string value associated with
            it.  The values are not converted from strings.
        '''
        pass

    def get_slabs(self):
        pass

    def flush_all(self):
        'Expire all data currently in the memcache servers.'
        pass


    def delete_multi(self, keys, time=0, key_prefix=''):
        '''
        Delete multiple keys in the memcache doing just one query.

        >>> notset_keys = mc.set_multi({'key1' : 'val1', 'key2' : 'val2'})
        >>> mc.get_multi(['key1', 'key2']) == {'key1' : 'val1', 'key2' : 'val2'}
        1
        >>> mc.delete_multi(['key1', 'key2'])
        1
        >>> mc.get_multi(['key1', 'key2']) == {}
        1


        This method is recommended over iterated regular L{delete}s as it reduces total latency, since
        your app doesn't have to wait for each round-trip of L{delete} before sending
        the next one.

        @param keys: An iterable of keys to clear
        @param time: number of seconds any subsequent set / update commands should fail. Defaults to 0 for no delay.
        @param key_prefix:  Optional string to prepend to each key when sending to memcache.
            See docs for L{get_multi} and L{set_multi}.

        @return: 1 if no failure in communication with any memcacheds.
        @rtype: int

        '''
        pass

    def delete(self, key, time=0):
        '''Deletes a key from the memcache.

        @return: Nonzero on success.
        @param time: number of seconds any subsequent set / update commands
        should fail. Defaults to 0 for no delay.
        @rtype: int
        '''
        pass

    def incr(self, key, delta=1):
        """
        Sends a command to the server to atomically increment the value
        for C{key} by C{delta}, or by 1 if C{delta} is unspecified.
        Returns None if C{key} doesn't exist on server, otherwise it
        returns the new value after incrementing.

        Note that the value for C{key} must already exist in the memcache,
        and it must be the string representation of an integer.

        >>> mc.set("counter", "20")  # returns 1, indicating success
        1
        >>> mc.incr("counter")
        21
        >>> mc.incr("counter")
        22

        Overflow on server is not checked.  Be aware of values approaching
        2**32.  See L{decr}.

        @param delta: Integer amount to increment by (should be zero or greater).
        @return: New value after incrementing.
        @rtype: int
        """
        pass

    def decr(self, key, delta=1):
        """
        Like L{incr}, but decrements.  Unlike L{incr}, underflow is checked and
        new values are capped at 0.  If server value is 1, a decrement of 2
        returns 0, not -1.

        @param delta: Integer amount to decrement by (should be zero or greater).
        @return: New value after decrementing.
        @rtype: int
        """
        pass



    def add(self, key, val, time = 0, min_compress_len = 0):
        '''
        Add new key with value.

        Like L{set}, but only stores in memcache if the key doesn't already exist.

        @return: Nonzero on success.
        @rtype: int
        '''
        pass

    def append(self, key, val, time=0, min_compress_len=0):
        '''Append the value to the end of the existing key's value.

        Only stores in memcache if key already exists.
        Also see L{prepend}.

        @return: Nonzero on success.
        @rtype: int
        '''
        pass

    def prepend(self, key, val, time=0, min_compress_len=0):
        '''Prepend the value to the beginning of the existing key's value.

        Only stores in memcache if key already exists.
        Also see L{append}.

        @return: Nonzero on success.
        @rtype: int
        '''
        pass

    def replace(self, key, val, time=0, min_compress_len=0):
        '''Replace existing key with value.

        Like L{set}, but only stores in memcache if the key already exists.
        The opposite of L{add}.

        @return: Nonzero on success.
        @rtype: int
        '''
        pass

    def set(self, key, val, time=0, min_compress_len=0):
        '''Unconditionally sets a key to a given value in the memcache.

        The C{key} can optionally be an tuple, with the first element
        being the server hash value and the second being the key.
        If you want to avoid making this module calculate a hash value.
        You may prefer, for example, to keep all of a given user's objects
        on the same memcache server, so you could use the user's unique
        id as the hash value.

        @return: Nonzero on success.
        @rtype: int
        @param time: Tells memcached the time which this value should expire, either
        as a delta number of seconds, or an absolute unix time-since-the-epoch
        value. See the memcached protocol docs section "Storage Commands"
        for more info on <exptime>. We default to 0 == cache forever.
        @param min_compress_len: The threshold length to kick in auto-compression
        of the value using the zlib.compress() routine. If the value being cached is
        a string, then the length of the string is measured, else if the value is an
        object, then the length of the pickle result is measured. If the resulting
        attempt at compression yeilds a larger string than the input, then it is
        discarded. For backwards compatability, this parameter defaults to 0,
        indicating don't ever try to compress.
        '''
        pass


    def cas(self, key, val, time=0, min_compress_len=0):
        '''Sets a key to a given value in the memcache if it hasn't been
        altered since last fetched. (See L{gets}).

        The C{key} can optionally be an tuple, with the first element
        being the server hash value and the second being the key.
        If you want to avoid making this module calculate a hash value.
        You may prefer, for example, to keep all of a given user's objects
        on the same memcache server, so you could use the user's unique
        id as the hash value.

        @return: Nonzero on success.
        @rtype: int
        @param time: Tells memcached the time which this value should expire,
        either as a delta number of seconds, or an absolute unix
        time-since-the-epoch value. See the memcached protocol docs section
        "Storage Commands" for more info on <exptime>. We default to
        0 == cache forever.
        @param min_compress_len: The threshold length to kick in
        auto-compression of the value using the zlib.compress() routine. If
        the value being cached is a string, then the length of the string is
        measured, else if the value is an object, then the length of the
        pickle result is measured. If the resulting attempt at compression
        yeilds a larger string than the input, then it is discarded. For
        backwards compatability, this parameter defaults to 0, indicating
        don't ever try to compress.
        '''
        pass

    def set_multi(self, mapping, time=0, key_prefix='', min_compress_len=0):
        '''
        Sets multiple keys in the memcache doing just one query.

        >>> notset_keys = mc.set_multi({'key1' : 'val1', 'key2' : 'val2'})
        >>> mc.get_multi(['key1', 'key2']) == {'key1' : 'val1', 'key2' : 'val2'}
        1


        This method is recommended over regular L{set} as it lowers the number of
        total packets flying around your network, reducing total latency, since
        your app doesn't have to wait for each round-trip of L{set} before sending
        the next one.

        @param mapping: A dict of key/value pairs to set.
        @param time: Tells memcached the time which this value should expire, either
        as a delta number of seconds, or an absolute unix time-since-the-epoch
        value. See the memcached protocol docs section "Storage Commands"
        for more info on <exptime>. We default to 0 == cache forever.
        @param key_prefix:  Optional string to prepend to each key when sending to memcache. Allows you to efficiently stuff these keys into a pseudo-namespace in memcache:
            >>> notset_keys = mc.set_multi({'key1' : 'val1', 'key2' : 'val2'}, key_prefix='subspace_')
            >>> len(notset_keys) == 0
            True
            >>> mc.get_multi(['subspace_key1', 'subspace_key2']) == {'subspace_key1' : 'val1', 'subspace_key2' : 'val2'}
            True

            Causes key 'subspace_key1' and 'subspace_key2' to be set. Useful in conjunction with a higher-level layer which applies namespaces to data in memcache.
            In this case, the return result would be the list of notset original keys, prefix not applied.

        @param min_compress_len: The threshold length to kick in auto-compression
        of the value using the zlib.compress() routine. If the value being cached is
        a string, then the length of the string is measured, else if the value is an
        object, then the length of the pickle result is measured. If the resulting
        attempt at compression yeilds a larger string than the input, then it is
        discarded. For backwards compatability, this parameter defaults to 0,
        indicating don't ever try to compress.
        @return: List of keys which failed to be stored [ memcache out of memory, etc. ].
        @rtype: list

        '''
        pass

    def get(self, key):
        '''Retrieves a key from the memcache.

        @return: The value or None.
        '''
        pass
    def gets(self, key):
        '''Retrieves a key from the memcache. Used in conjunction with 'cas'.

        @return: The value or None.
        '''
        pass
        
    def get_multi(self, keys, key_prefix=''):
        '''
        Retrieves multiple keys from the memcache doing just one query.

        >>> success = mc.set("foo", "bar")
        >>> success = mc.set("baz", 42)
        >>> mc.get_multi(["foo", "baz", "foobar"]) == {"foo": "bar", "baz": 42}
        1
        >>> mc.set_multi({'k1' : 1, 'k2' : 2}, key_prefix='pfx_') == []
        1

        This looks up keys 'pfx_k1', 'pfx_k2', ... . Returned dict will just have unprefixed keys 'k1', 'k2'.
        >>> mc.get_multi(['k1', 'k2', 'nonexist'], key_prefix='pfx_') == {'k1' : 1, 'k2' : 2}
        1

        get_mult [ and L{set_multi} ] can take str()-ables like ints / longs as keys too. Such as your db pri key fields.
        They're rotored through str() before being passed off to memcache, with or without the use of a key_prefix.
        In this mode, the key_prefix could be a table name, and the key itself a db primary key number.

        >>> mc.set_multi({42: 'douglass adams', 46 : 'and 2 just ahead of me'}, key_prefix='numkeys_') == []
        1
        >>> mc.get_multi([46, 42], key_prefix='numkeys_') == {42: 'douglass adams', 46 : 'and 2 just ahead of me'}
        1

        This method is recommended over regular L{get} as it lowers the number of
        total packets flying around your network, reducing total latency, since
        your app doesn't have to wait for each round-trip of L{get} before sending
        the next one.

        See also L{set_multi}.

        @param keys: An array of keys.
        @param key_prefix: A string to prefix each key when we communicate with memcache.
            Facilitates pseudo-namespaces within memcache. Returned dictionary keys will not have this prefix.
        @return:  A dictionary of key/value pairs that were available. If key_prefix was provided, the keys in the retured dictionary will not have it present.

        '''
        pass

    def check_key(self, key, key_extra_len=0):
        """Checks sanity of key.  Fails if:
            Key length is > SERVER_MAX_KEY_LENGTH (Raises MemcachedKeyLength).
            Contains control characters  (Raises MemcachedKeyCharacterError).
            Is not a string (Raises MemcachedStringEncodingError)
            Is an unicode string (Raises MemcachedStringEncodingError)
            Is not a string (Raises MemcachedKeyError)
            Is None (Raises MemcachedKeyError)
        """
        pass