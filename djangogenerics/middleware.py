from django.conf import settings
import re
import logging

LOG = logging.getLogger(__name__)

class iPhoneMiddleware(object):
    """
    If the Middleware detects an iPhone/iPod the template dir changes to the
    iPhone template folder.
    """

    def __init__(self):
        self.normal_templates = settings.TEMPLATE_DIRS
        self.iphone_templates = (settings.TEMPLATE_DIRS[0] + '/iphone', settings.TEMPLATE_DIRS[0])

    def process_request(self, request):
        p = re.compile('iPhone|iPod', re.IGNORECASE)
        
        try:
            if p.search(request.META['HTTP_USER_AGENT']):
                # user agent looks like iPhone or iPod
                settings.TEMPLATE_DIRS = self.iphone_templates
                LOG.debug('Setting template dir to iphone/')
            else:
                # other user agents
                settings.TEMPLATE_DIRS = self.normal_templates
                LOG.debug('leaving template dir set to normal')
        except:
            # other user agents
            settings.TEMPLATE_DIRS = self.normal_templates
            LOG.info('Error occured while switching template directories')
        
        return

