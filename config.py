from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

class Config():
    def __init__(self, configfile='./site.conf'):
        self.config = SafeConfigParser()
        self.config.read(configfile)
        self.configfile = configfile
        self.database = dict()
        self.user = dict()
        self.forum = dict()

        if self.config.has_section('database'):
            try:
                self.database['user'] = self.config.get('database', 'user')
                self.database['pass'] = self.config.get('database', 'pass')
                self.database['host'] = self.config.get('database', 'host')
                self.database['db'] = self.config.get('database', 'db')   
            except:
                self.database['user'] = None
                self.database['host'] = None
                self.database['pass'] = None
                self.database['db'] = None

        if self.config.has_section('user'):
            try:
                self.user['backend'] = self.config.get('user', 'backend')
            except:
                self.user['backend'] = mysql

        if self.config.has_section('forum'):
            try:
                self.forum['index'] = int(self.config.get('forum', 'index'))
            except:
                self.user['index'] = 0
