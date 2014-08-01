#!/usr/bin/env python
# -*- coding:utf-8 -*-

import jinja2
import os
import webapp2
import logging

from functools import wraps

from google.appengine.api import images
from google.appengine.api import mail
from google.appengine.api import memcache
# from google.appengine.api import urlfetch
# from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.runtime import apiproxy_errors

from webapp2_extras import i18n
from webapp2_extras import sessions
from webapp2_extras import sessions_memcache

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               extensions=['jinja2.ext.i18n'],
                               autoescape=True)
JINJA_ENV.install_gettext_translations(i18n)


def rate_limit(seconds_per_request=1):
    def rate_limiter(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            added = memcache.add('%s:%s' %
                                 (self.__class__.__name__,
                                  self.request.remote_addr or ''), 1,
                                 time=seconds_per_request,
                                 namespace='rate_limiting')

            if not added:
                self.response.write('Rate limit exceeded')
                self.response.set_status(403)
                return
            return function(self, *args, **kwargs)
        return wrapper
    return rate_limiter


def parseAcceptLanguage(acceptLanguage):
    languages = acceptLanguage.split(",")
    locale_q_pairs = []

    for language in languages:
        if language.split(";")[0] == language:
            # no q => q = 1
            locale_q_pairs.append((language.strip(), "1"))
        else:
            locale = language.split(";")[0].strip()
            q = language.split(";")[1].split("=")[1]
            locale_q_pairs.append((locale, q))

    return locale_q_pairs


supported_locales = ['no', 'nb', 'nn', 'en']


def detectLocale(acceptLanguage):
    default_locale = 'en'
    locale_q_pairs = parseAcceptLanguage(acceptLanguage)
    for pair in locale_q_pairs:
        for locale in supported_locales:
            # pair[0] is locale, pair[1] is q value
            if pair[0].replace('-', '_').lower().startswith(locale.lower()):
                return locale
    return default_locale


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    @classmethod
    def render_str(cls, template, *a, **params):
        template = JINJA_ENV.get_template(template)
        return template.render(params)

    def render(self, template, locale=None, *a, **params):
        if not locale:
            locale = self.session.get('locale')
        if not locale:
            locale = detectLocale(self.request.headers.get('accept_language'))
        i18n.get_i18n().set_locale(locale)
        self.write(self.render_str(template, locale=locale, *a, **params))

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(name='navette_session',
                                              factory=sessions_memcache.
                                              MemcacheSessionFactory)


class ChangeLocale(Handler):
    def get(self, locale):
        path = '/' + locale + '/'
        self.session['locale'] = locale
        self.redirect(path)


class EditProductHandler(Handler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.render('edit_product.html', upload_url=upload_url)


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        image = (images.get_serving_url(resource, 32))
        if image:
            self.response.out.write("%s" % image)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())


# class ThumbnailHandler(blobstore_handlers.BlobstoreDownloadHandler):
#     def get(self, resource):
#         resource = str(urllib.unquote(resource))
#         blob_info = blobstore.BlobInfo.get(resource)
#
#         size = self.request.get('size')
#         size = int(size) if size else 100
#
#         if blob_info:
#             img = images.Image(blob_key=resource)
#             img.resize(width=size, height=size)
#             thumbnail = img.execute_transforms(output_encoding=images.JPG)
#
#             self.response.headers['Content-Type'] = 'image/jpg'
#             self.response.out.write(thumbnail)
#             return
#
#         # Either the blob key was not provided or there was no value with
#         # ID in the Blobstore
#         self.error(404)


class FourHandler(Handler):
    def get(self, locale):
        self.render("404.html", locale=locale)


class HomeHandler(Handler):
    def get(self, locale):
        self.render("home.html", locale=locale)


class BoatHandler(Handler):
    def get(self, locale):
        self.render('boats.html', locale=locale)


class S540Handler(Handler):
    def get(self, locale):
        self.render('s540.html', locale=locale)


class S565Handler(Handler):
    def get(self, locale):
        self.render('s565.html', locale=locale)


class ContactHandler(Handler):
    def get(self, locale):
        self.render('contact.html', locale=locale)


class AboutHandler(Handler):
    def get(self, locale):
        self.render('about.html', locale=locale)


class AutoHandler(Handler):
    def get(self, locale):
        self.render('automotive.html', locale=locale)


class AmarokHandler(Handler):
    def get(self, locale):
        self.render("amarok.html", locale=locale)


class HiluxHandler(Handler):
    def get(self, locale):
        self.render("hilux.html", locale=locale)


class SiteMapHandler(Handler):
    def get(self):
        self.render('sitemap.html')


class MailHandler(Handler):
    @rate_limit(seconds_per_request=15)
    def post(self):
        user_name = self.request.get('name')
        user_email = self.request.get('email')
        location = self.request.get('location')
        message = self.request.get('msg')
        product = self.request.get('product')
        if user_name:
            message += " - %s" % user_name
        if product:
            message += "Product: %s " % product
        if location:
            message += " User location: %s" % location
        from_addr = "info@saldusgaisma.lv"
        to_addr = "nejeega@gmail.com"

        try:
            msg = mail.EmailMessage()
            msg.sender = from_addr
            msg.to = to_addr
            msg.subject = "Sent from navette.no by user %s" % user_email
            msg.html = message
            msg.send()
            self.redirect(self.request.referer)
        except apiproxy_errors.OverQuotaError, message:
            logging.error(message)


# Webapp2 config
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'navettes-not-so-secret-key',
    'name': 'navette_session',
}
config['webapp2_extras.i18n'] = {
    'translations_path': 'locale',
}

# Locale regex
l = '(?:/([a-z]{2}))?'
# Trailing slash regex
ts = '(?:/)?'

app = webapp2.WSGIApplication([
    (l + '/s540' + ts, S540Handler),
    (l + '/s565' + ts, S565Handler),
    (l + '/amarok' + ts, AmarokHandler),
    (l + '/hilux' + ts, HiluxHandler),
    (l + '/boats' + ts, BoatHandler),
    (l + '/automotive' + ts, AutoHandler),
    (l + '/contact' + ts, ContactHandler),
    (l + '/about' + ts, AboutHandler),
    (l + '/sitemap' + ts, SiteMapHandler),
    (l + '/', HomeHandler),
    ('/locale/([a-z]{2})' + ts, ChangeLocale),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/mail', MailHandler),
    (l + '/.*' + ts, FourHandler),
], config=config, debug=True)
