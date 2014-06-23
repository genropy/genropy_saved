from gnr.core.gnrbag import Bag, BagCbResolver

def hello(x=''):
    return 'i say : %s ' % x

b = Bag()
b.setCallBackItem('say_hello', hello, x='hello')
b.setCallBackItem('say_muu', hello, x='muu')
b.setCallBackItem('say_buzbuz', hello, x='buzbuz')
resolver = BagCbResolver(hello, x='fatto da resolver e non da setCallBackItem')
b.setItem('say_resolver', resolver)

print b['say_hello']
print b['say_muu']
print b['say_buzbuz']
print b['say_resolver']