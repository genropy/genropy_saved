# encoding: utf-8

from __future__ import print_function
def main(db):
    print('0001 set error_msg and error_ts fields if sending_attempt')
    def cb(r):
        sending_attempt = r['sending_attempt']
        last_n = sending_attempt.nodes[-1]
        r['error_msg'] = last_n.getAttr('error')
        r['error_ts'] = last_n.getAttr('ts')

    db.table('email.message').batchUpdate(cb, where="""$sending_attempt IS NOT NULL AND 
                                                       $error_msg IS NULL AND $send_date IS NULL""")