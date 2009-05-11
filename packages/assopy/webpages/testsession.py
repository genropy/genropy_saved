from mod_python import apache, Session
def index(req):
    session = Session.Session(req)

    try:
        session['hits'] += 1
    except:
        session['hits'] = 1

    session.save()

    req.content_type = 'text/plain'
    req.write('Hits: %d\n' % session['hits'])
    return apache.OK