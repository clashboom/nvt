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
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.runtime import apiproxy_errors

from webapp2_extras import sessions
from webapp2_extras import sessions_memcache

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)


# Webapp2 Sessions config
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'navettes-not-so-secret-key',
    'name': 'navette_session',
}


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

            return function
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


def detectLocale(acceptLanguage):
    defaultLocale = 'en'
    supportedLocales = ['no', 'nb', 'nn', 'en']

    locale_q_pairs = parseAcceptLanguage(acceptLanguage)
    for pair in locale_q_pairs:
        for locale in supportedLocales:
            # pair[0] is locale, pair[1] is q value
            if pair[0].replace('-', '_').lower().startswith(locale.lower()):
                return locale

    return defaultLocale


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    @classmethod
    def render_str(cls, template, *a, **params):
        template = JINJA_ENV.get_template(template)
        return template.render(params)

    def render(self, template, *a, **params):
        locale = self.session.get('locale')
        # norsk = ['no', 'nb', 'nn']
        if not locale:
            locale = detectLocale(self.request.headers.get('accept_language'))
            self.session['locale'] = locale
            path = self.request.referer
            self.redirect(path if path else '/')
        elif locale == 'en':
            template = template[:-5] + '_' + 'en' + '.html'
        locale = self.request.headers.get('accept_language')
        self.write(self.render_str(template,
                                   locale=locale,
                                   *a, **params))

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
        if locale == 'en':
            self.session['locale'] = locale
        elif locale == 'no':
            self.session['locale'] = locale
        else:
            self.redirect(self.request.referer)
        self.redirect(self.request.referer)


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


class MainHandler(Handler):
    def get(self):
        self.render('home.html')


class BoatHandler(Handler):
    def get(self):
        self.render('boats.html')


class S540Handler(Handler):
    def get(self):
        self.render('s540.html')


class S565Handler(Handler):
    def get(self):
        self.render('s565.html')


class ContactHandler(Handler):
    def get(self):
        self.render('contact.html')


class AboutHandler(Handler):
    def get(self):
        self.render('about.html')


class AutoHandler(Handler):
    def get(self):
        self.render('automotive.html')


class AmarokHandler(Handler):
    def get(self):
        self.render("amarok.html")


class HiluxHandler(Handler):
    def get(self):
        self.render("hilux.html")


class Product(ndb.Model):
    name = ndb.StringProperty(required=True)
    template = ndb.StringProperty()

    @property
    def pictures(self):
        return Gallery.query(Gallery.product == self.name)


class Gallery(ndb.Model):
    product = ndb.StringProperty(required=True)
    pictures = ndb.BlobKeyProperty(repeated=True)


class ProductHandler(Handler):
    def get(self, product):
        product = Product.query(Product.name == product).get()

        if product:
            self.render(product.template)

        self.error(404)


class SiteMapHandler(Handler):
    def get(self):
        self.render('sitemap.html')


class MailHandler(Handler):
    @rate_limit(seconds_per_request=15)
    def post(self):
        user_email = self.request.get('email')
        message = self.request.get('msg')
        from_addr = "info@saldusgaisma.lv"
        to_addr = "nejeega@gmail.com"

        try:
            msg = mail.EmailMessage()
            msg.sender = from_addr
            msg.to = to_addr
            msg.subject = "Sent from page by user %s" % user_email
            msg.html = message

            msg.send()
        except apiproxy_errors.OverQuotaError, message:
            logging.error(message)


app = webapp2.WSGIApplication([
    ('(?:/maritim.?)?/s540', S540Handler),
    ('(?:/maritim.?)?/s565', S565Handler),
    ('/amarok', AmarokHandler),
    ('/hilux', HiluxHandler),
    ('/maritim.?', BoatHandler),
    ('/boats', BoatHandler),
    ('/auto', AutoHandler),
    ('/contact', ContactHandler),
    ('/about', AboutHandler),
    ('/locale(?:/)?(.*)?', ChangeLocale),
    # ('/edit', EditProductHandler),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/product/([^/]+)?', ProductHandler),
    ('/sitemap', SiteMapHandler),
    ('/.*', MainHandler),
], config=config, debug=True)
