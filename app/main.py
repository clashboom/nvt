#!/usr/bin/env python
# -*- coding:utf-8 -*-

import jinja2
import os
import webapp2

from google.appengine.api import memcache

from google.appengine.ext import ndb

from webapp2_extras import sessions
from webapp2_extras import sessions_memcache

from functools import wraps

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
    # defaultLocale = 'en_US'
    defaultLocale = 'no'
    # supportedLocales = ['no', 'en']

    # locale_q_pairs = parseAcceptLanguage(acceptLanguage)
    # for pair in locale_q_pairs:
    #     for locale in supportedLocales:
    #         # pair[0] is locale, pair[1] is q value
    #         if pair[0].replace('-', '_').lower().startswith(locale.lower()):
    #             return locale

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
        if not locale:
            locale = detectLocale(self.request.headers.get('accept_language'))
            self.session['locale'] = locale
        elif locale != 'no':
            template = template[:-5] + '_' + 'en' + '.html'
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


app = webapp2.WSGIApplication([
    ('/s540', S540Handler),
    ('/s565', S565Handler),
    ('/amarok', AmarokHandler),
    ('/hilux', HiluxHandler),
    ('/boats', BoatHandler),
    ('/auto', AutoHandler),
    ('/contact', ContactHandler),
    ('/about', AboutHandler),
    ('/locale(?:/)?(.*)?', ChangeLocale),
    ('/.*', MainHandler),
], config=config, debug=True)
