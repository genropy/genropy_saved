#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 

from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.utils import old_div
#from builtins import object
try:
    import memcache

    HAS_MEMCACHE = True
except ImportError:
    HAS_MEMCACHE = False

import pickle as pickle
import os

from datetime import timedelta
import time
from threading import RLock
import _thread

MAX_RETRY = 500
DEBUG_LIMIT = 50
RETRY_TIME = 0.01
LOCK_TIME = 2


def exp_to_epoch(expiry):
    if not expiry:
        return 0
    if hasattr(expiry, 'timetuple'):
        return int(time.mktime(expiry.timetuple()))
    if isinstance(expiry, timedelta):
        expiry = expiry.days * 86400 + expiry.seconds
    return int(time.time() + expiry)

def locked_storage(func):
    def decore(self, *args, **kwargs):
        with self.storage_lock:
            result = func(self, *args, **kwargs)
            return result
    return decore
    
class SharedLocker(object):
    def __init__(self, sd, key, max_retry=MAX_RETRY,
                 lock_time=LOCK_TIME,
                 retry_time=RETRY_TIME,caller=None,reason=None):
        self.sd = sd
        self.key = key
        self.max_retry = max_retry
        self.lock_time = lock_time
        self.retry_time = retry_time
        self.caller = caller
        self.reason = reason

    def __enter__(self):
        self.timer_start = time.time()
        self.sd.lock(self.key, lock_time=self.lock_time,
                     max_retry=self.max_retry,
                     retry_time=self.retry_time)
        self.timer_getlock = time.time()-self.timer_start
        return self.sd

    def __exit__(self, exception_type, value, traceback):
        self.timer_exec = time.time() - self.timer_start - self.timer_getlock
        if exception_type:
            print('error in locking execution %s' %self)
        elif self.timer_exec>.5:
            print('Long locking time %s' %self)
        return self.sd.unlock(self.key)

    def __str__(self):
        return 'Locker: Key %s, Caller: %s, Reason: %s,  Getlock time: %f, Exec time %f' %(self.key, self.caller or '', self.reason or '', self.timer_getlock, self.timer_exec)
        
class GnrSharedData(object):
    """TODO"""
    def __init__(self, site):
        self.site = site
        self._locks = {}

    def locked(self, key, max_retry=MAX_RETRY, lock_time=LOCK_TIME, retry_time=RETRY_TIME, caller=None, reason=None):
        """TODO"""
        return SharedLocker(self, key, lock_time=lock_time,
                            max_retry=max_retry,
                            retry_time=retry_time, caller=caller, reason=reason)

    def lockcount(self, key, delta):
        lockdict = self._locks.setdefault(_thread.get_ident(), {})
        lockdict[key] = lockcount = max(0, lockdict.get(key, 0) + delta)
        return lockcount

    def unlock(self, key):
        if self.lockcount(key, -1) == 0:
            return self.delete('%s_lock' % key)

    def lock(self, key, max_retry=None,
             lock_time=None,
             retry_time=None):
        if self.lockcount(key, 1) > 1:
            return True
        max_retry = max_retry or MAX_RETRY
        k = max_retry
        lock_time = lock_time or LOCK_TIME
        retry_time = retry_time or RETRY_TIME
        while k:
            if self.add('%s_lock' % key, True, expiry=lock_time):
                if max_retry - k > DEBUG_LIMIT:
                    print("TRIED TO LOCK AND GOT AFTER: %f" % (old_div((max_retry-k), RETRY_TIME)))
                return True
            k -= 1
            time.sleep(retry_time)
        print('************UNABLE TO LOCK : %s max_retry:%i***************' % (key, max_retry))

    def dump(self):
        pass

    def load(self):
        pass

    def flush_all(self):
        pass

class GnrSharedData_dict(GnrSharedData):
    STORAGE_PATH = 'shared_data.pik'
    
    def __init__(self, site):
        super(GnrSharedData_dict, self).__init__(site)
        self.storage = {}
        self.storage_lock = RLock()
        self.cas_id = 0
        self.storage_path = os.path.join(self.site.site_path, self.STORAGE_PATH)
        if os.path.exists(self.storage_path):
            self.load()
            
    def dump(self):
        """TODO"""
        print('DUMP SHARED DATA')
        with open(self.storage_path, 'w') as shared_data_file:
            pickle.dump(self.storage, shared_data_file)

    def load(self):
        try:
            with open(self.storage_path) as shared_data_file:
                self.storage = pickle.load(shared_data_file)
                print('LOAD SHARED DATA')
        except EOFError:
            print('UNABLE TO LOAD SHARED DATA')
        os.remove(self.storage_path)

    def key(self, key):
        return key

    def _get_next_cas_id(self):
        self.cas_id += 1
        return self.cas_id

    next_cas_id = property(_get_next_cas_id)

    @locked_storage
    def set(self, key, value, expiry=0, cas_id=None):
        expiry = exp_to_epoch(expiry)
        if cas_id is None:
            pickled_value = pickle.dumps(value)
            self.storage[key] = (pickled_value, expiry, self.next_cas_id)
            return True
        else:
            previous_cas_id = self.storage.get(key, (None, None, None))[2]
            if previous_cas_id != cas_id:
                result = False
            else:
                pickled_value = pickle.dumps(value)
                self.storage[key] = (pickled_value, expiry, self.next_cas_id)
                result = True
            return result

    def gets(self, key):
        return self._get(key)

    def get(self, key):
        return self._get(key)[0]

    @locked_storage
    def _get(self, key):
        pickled_value, expiry, cas_id = self.storage.get(key, (None, None, None))
        if expiry and time.time() > expiry:
            self.delete(key)
            value, cas_id = None, None
        else:
            value = pickled_value and pickle.loads(pickled_value)
        return value, cas_id

    def delete(self, key):
        self.storage.pop(key, None)

    @locked_storage
    def incr(self, key, delta=1):
        value, cas_id = self.gets(key)
        if cas_id:
            if not type(value) == int:
                value = int(value)
            value = value + delta
            value, self.set(key, value, cas_id=cas_id)
        return value

    @locked_storage
    def decr(self, key, delta=1):
        value, cas_id = self.gets(key)
        if cas_id:
            if not type(value) == int:
                value = int(value)
            value = value + delta
            if value < 0:
                value = 0
            self.set(self, key, value, cas_id=cas_id)
        return value

    @locked_storage
    def add(self, key, value, expiry=0):
        if self.gets(key) == (None, None):
            self.set(key, value, expiry=expiry)
            result = True
        else:
            result = False
        return result

    @locked_storage
    def replace(self, key, value, expiry=0):
        if not self.gets(key) == (None, None):
            self.set(key, value, expiry=expiry)
            result = True
        else:
            result = False
        return result

    @locked_storage
    def get_multi(self, keys, key_prefix=''):
        result = {}
        for k in keys:
            val, cas_id = self.gets('%s%s' % (key_prefix, str(k)))
            if cas_id:
                result[k] = val
        return result

    def flush_all(self):
        self.storage = {}

    def disconnect_all(self):
        pass

class GnrSharedData_memcache(GnrSharedData):
    """TODO"""
    def __init__(self, site, memcache_config=None, debug=None):
        """initialize the shared data store from memcache_config."""
        super(GnrSharedData_memcache, self).__init__(site)
        self._namespace = site.site_name
        server_list = ['%(host)s:%(port)s' % attr for attr in memcache_config.digest('#a')]
        self.storage = memcache.Client(server_list, debug=debug)
        self.visited_keys = {} #MIKI:not used Do we really need it?
        self._test(False)

    def disconnect_all(self):
        """TODO"""
        self.storage.disconnect_all()

    def _test(self, doraise=True):
        if not self.storage.get_stats():
            if doraise:
                raise self.site.exception('memcached not started')
            else:
                print('****** memcached not started ********')

    def key(self, key):
        """TODO"""
        prefixed_key = ('%s_%s' % (self._namespace, key)).encode('utf8')
        self.visited_keys[prefixed_key] = key
        return prefixed_key  #MIKI: why don't we strip the result?

    def debug_keys(self):
        for key in list(self.visited_keys.values()):
            print(self.get(key))

    def get(self, key):
        prefixed_key = self.key(key).strip()
        return self.storage.get(prefixed_key)

    def gets(self, key):
        result = self.storage.gets(self.key(key))
        cas_id = self.storage.cas_ids.get(self.key(key))
        return result, cas_id

    def set(self, key, value, expiry=0, cas_id=None):
        prefixed_key = self.key(key).strip()
        if not cas_id:
            set_ok = self.storage.set(prefixed_key, value, time=exp_to_epoch(expiry))
            if not set_ok:
                self._test()
        else:
            self.storage.cas_ids[prefixed_key] = cas_id
            self.storage.cas(prefixed_key, value, time=exp_to_epoch(expiry))
            # MIKI:we are not testing the result of this cas
            # what happen if the cas is not respected
            # no clash advice. Don't we need it?

    def add(self, key, value, expiry=0):
        status = self.storage.add(self.key(key), value, time=exp_to_epoch(expiry))
        if status:
            return value
        else:
            print('wrong status unable to add in memcache %s' %key)

    def replace (self, key, value, expiry=0):
        status = self.storage.replace(self.key(key), value, time=exp_to_epoch(expiry))
        if status:
            return value

    def delete(self, key):
        self.storage.delete(self.key(key), None)

    def incr(self, key, delta=1):
        return self.storage.incr(self.key(key), delta=delta)

    def decr(self, key, delta=1):
        return self.storage.decr(self.key(key), delta=delta)

    def get_multi(self, keys, key_prefix=''):
        key_prefix = '%s_%s' % (self._namespace, key_prefix)
        key_prefix = key_prefix.encode('utf8')
        return self.storage.get_multi(keys, key_prefix)

    def flush_all(self):
        self.storage.flush_all()
        self.visited_keys = {}

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


    def add(self, key, val, time=0, min_compress_len=0):
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
        
