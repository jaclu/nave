import logging
import os
from os.path import abspath, dirname
import zipfile

from django.template import Context
from django.template.loader import get_template
from django.views.generic import DetailView
from django_downloadview import PathDownloadView

from django.core import urlresolvers

from .models import DiwInstance


logger = logging.getLogger(__name__)


# @login_required
class DiwInstanceView(DetailView):
    template_name = 'diw.html'
    context_object_name = 'diw'
    model = DiwInstance

    # def get_admin_url(self):
    #     return urlresolvers.reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.module_name), args=(self.id,))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DiwInstanceView, self).get_context_data(**kwargs)
        # context['diw_admin_link'] = self.get_admin_url()
        return context


class DiwConfigView(DetailView):
    template_name = 'diw-config.js'
    context_object_name = 'diw'
    model = DiwInstance


class DiwDownload(PathDownloadView):
    """Create a diw download. """

    def get_path(self):
        slug = self.kwargs.get('slug')
        config = get_template('diw-config.js').render(
            Context({
                'diw': DiwInstance.objects.get(slug=slug)
            })
        )
        diw_name = self.kwargs.get('slug', 'diw')
        print(diw_name)
        diw_path_zip = '/tmp/{}.zip'.format(diw_name)
        # todo turn into in memory creation
        with zipfile.ZipFile(diw_path_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            diw_path = os.path.join(dirname(abspath(__file__)), 'diw_dist')
            for dir_name, subdirs, files in os.walk(diw_path):
                for filename in files:
                    absname = os.path.abspath(os.path.join(dir_name, filename))
                    arcname = absname[len(diw_path) + 1:]
                    logger.info('zipping %s as %s' % (os.path.join(dir_name, filename), arcname))
                    # todo fix this issues with expecting string but got bytes
                    zf.write(absname, arcname)
            # write configuration file
            zf.writestr('delving-instant-config-'+diw_name+'.js ', config)
        return diw_path_zip

