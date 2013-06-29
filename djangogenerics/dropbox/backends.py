import os
import logging

logger = logging.getLogger(__name__)

class DropboxTokenStorage:
    def load(self):
        pass

    def save(self, token):
        pass

    def remove(self):
        pass


class FileStorage(DropboxTokenStorage):
    def __init__(self, tokenfile):
        self.TOKEN_FILE = tokenfile

    def load(self):
        logger.info('Loading token from %s', self.TOKEN_FILE)
        try:
            token_file = open(self.TOKEN_FILE)
        except IOError:
            logger.warn('Could not find token in store')
            return False
        token = token_file.read().split('|')
        token_file.close()
        logger.debug('Token loaded')
        return token

    def save(self, key, secret):
        logger.debug('Saving token to file: %s', self.TOKEN_FILE)
        try:
            token_file = open(self.TOKEN_FILE, 'w')
        except IOError:
            logger.error('Could not open token store - %s', self.TOKEN_FILE)
            return False
        else:
            token_file.write("|".join([key, secret]))
            token_file.close()
            logger.info('Successfully stored token to file.')
        return True

    def remove(self):
        logger.debug('Removing token from file system (%s)', self.TOKEN_FILE)
        try:
            os.unlink(self.TOKEN_FILE)
        except IOError:
            logger.warn('The file %s did not exist. So no token.', self.TOKEN_FILE)
        else:
            logger.info('Token was successfully removed')
        return True
