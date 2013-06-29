from djangogenerics.dropbox.session import DropboxSession

class StoredDropboxSession(DropboxSession):
    def __init__(self, *args, **kwargs):
        self.backend = kwargs.pop('backend')
        super(StoredDropboxSession, self).__init__(*args, **kwargs)

    def load_from_store(self):
        token = self.backend.load()
        if token:
            self.set_token(*token)
            return True
        else:
            return False

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        print "Url:", url
        print "Please authorize in the browser. After you're done, press enter."
        raw_input()

        self.obtain_access_token(request_token)
        self.backend.save(self.token.key, self.token.secret)

    def unlink(self):
        self.backend.remove()
        super(StoredDropboxSession, self).unlink()
