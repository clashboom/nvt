#!/usr/bin/env python
# -*- coding:utf-8 -*-

import jinja2
import os
import webapp2

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    @classmethod
    def render_str(cls, template, *a, **params):
        template = JINJA_ENV.get_template(template)
        return template.render(params)

    def render(self, template, *a, **params):
        self.write(self.render_str(template, *a, **params))


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


class AutoHandler(Handler):
    def get(self):
        self.render('automotive.html')


app = webapp2.WSGIApplication([
    ('/s540', S540Handler),
    ('/s565', S565Handler),
    ('/boats', BoatHandler),
    ('/auto', AutoHandler),
    ('/contact', ContactHandler),
    ('/.*', MainHandler),
], debug=True)
