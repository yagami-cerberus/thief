# -*- mode: python -*-
a = Analysis(['.\\manage.py'],
             pathex=['.'],
             hiddenimports=[
                'django.test',
                'django.utils.six',
                'thief.auction.templatetags',
                'thief.auction.templatetags.keywords',
                'thief.bootstrap3.templatetags',
                'thief.bootstrap3.templatetags.bootstrap3',
                'thief.vendors.management.commands.vendor',
                'ConfigParser',
                'copy_reg',
                'cookielib',
                'Cookie',
                'htmlentitydefs',
                'HTMLParser',
                'httplib',
                'email',
                'email.mime',
                'BaseHTTPServer',
                'CGIHTTPServer',
                'SimpleHTTPServer',
                'cPickle',
                'Queue',
                'repr',
                'SocketServer',
                'thread',
                'markupbase', # FROM HTMLParser!!
                'django.contrib.sessions.serializers',
                'django.templatetags.cache',
                'django.templatetags.future',
                'django.templatetags.i18n',
                'django.templatetags.l10n',
                'django.templatetags.static',
                'django.templatetags.tz',
                'lxml.objectify',
                'lxml.etree',
                'lxml._elementpath',
                'amazonproduct.processors',
                'amazonproduct.processors._lxml',
                'amazonproduct.processors.elementtree',
                'amazonproduct.processors.etree',
                'amazonproduct.processors.objectify',
                'amazonproduct.contrib',
                'amazonproduct.contrib.cart',
                'amazonproduct.contrib.caching',
             ],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='server.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='thief')
