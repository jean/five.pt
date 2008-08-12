import os
import sys

from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_inner
from Acquisition import Implicit
from Globals import package_home
from OFS.Traversable import Traversable

from Products.PageTemplates.Expressions import SecureModuleImporter

import z3c.pt.pagetemplate


class ZopeViewPageTemplateFile(
    z3c.pt.pagetemplate.PageTemplateFile,
    Implicit,
    Traversable):

    default_expression = 'path'


class ViewPageTemplateFile(property):

    def __init__(self, filename, **kwargs):
        path = self.get_path_from_prefix(None)
        filename = os.path.join(path, filename)
        self.template = ZopeViewPageTemplateFile(filename)
        property.__init__(self, self.render)

    def get_path_from_prefix(self, _prefix):
        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(2).f_globals
            path = package_home(_prefix)
        return path

    def render(self, view):
        try:
            root = self.getPhysicalRoot()
        except AttributeError:
            try:
                root = view.context.getPhysicalRoot()
            except AttributeError:
                root = None

        context = aq_inner(view.context)

        def template(**kwargs):
            return self.template.render(
                view=view,
                context=context,
                request=view.request,
                _context=view.request,
                template=self,
                here=context,
                container=context,
                nothing=None,
                root=root,
                modules=SecureModuleImporter,
                views=ViewMapper(context, view.request),
                options=kwargs)

        return template

    def __call__(self):
        return self.render()
