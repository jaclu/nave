from collections import OrderedDict

import six
from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.xmlutils import SimplerXMLGenerator
from rdflib import Graph
from rest_framework import renderers
from rest_framework.renderers import BaseRenderer
from six import StringIO

from lod.utils.rdfstore import get_namespace_manager


class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    item_tag_name = 'list-item'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, encoding=self.charset)
        xml.startDocument()

        self._to_xml(xml, data)

        xml.endDocument()
        return stream.getvalue()

    def _get_namespace_prefix(self, search_label):
        if "_" in search_label:
            return search_label.split('_')[0]
        return None

    @staticmethod
    def _get_uri_from_search_label(search_label):
        if "_" in search_label:
            prefix, *label = search_label.split('_')
            uri = settings.RDF_SUPPORTED_PREFIXES.get(prefix, None)
            if uri:
                uri = uri[0].rstrip('/')
            else:
                return None
            return prefix, uri, "_".join(label)
        return None

    @staticmethod
    def normalize_attribute(value):
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _create_inner_tag_name(key):
        return key.lower() if not key.endswith('s') else key.lower()[:-1]

    def _to_xml(self, xml, data, tag_name=item_tag_name):
        if isinstance(data, (list, tuple)):
            for item in data:
                if tag_name == self.item_tag_name:
                    test = 1
                if tag_name is None:
                    self._to_xml(xml, item)
                elif isinstance(item, tuple):
                    search_label = item[0]
                    value = item[1]
                    prefix, ns, label = self._get_uri_from_search_label(search_label)
                    full_uri = ns, label
                    xml.startPrefixMapping(prefix, ns)
                    qname = search_label.replace('_', ":")
                    xml.startElementNS(full_uri, qname, {})
                    self._to_xml(xml, value)
                    xml.endElementNS(full_uri, qname)
                    xml.endPrefixMapping(prefix)
                elif tag_name in ['breadcrumb', 'link']:
                    has_text = False
                    output = None
                    output_keys = [key for key in item.keys() if key in ['display', 'pageNumber', 'displayString']]
                    if output_keys:
                        for key in output_keys:
                            output = item.pop(key)
                    attr = {key: self.normalize_attribute(value) for key, value in item.items()}
                    xml.startElement(tag_name, attr)
                    xml.characters(smart_text(output))
                    xml.endElement(tag_name)
                else:
                    xml.startElement(tag_name, {})
                    self._to_xml(xml, item)
                    xml.endElement(tag_name)
        elif isinstance(data, dict):
            for key, value in six.iteritems(data):
                # if value is ordered dict use key singular as list-item
                xml.startElement(key, {})
                if value and isinstance(value, list) and isinstance(value[0], OrderedDict):
                    tag_name = self._create_inner_tag_name(key)
                    if tag_name in ['item', 'field', 'relateditem'] and 'i18n' not in value[0].keys():
                        tag_name = None
                    self._to_xml(xml, value, tag_name=tag_name)
                elif isinstance(value, OrderedDict) and key in ['fields']:
                    tag_name = self._create_inner_tag_name(key)
                    new_list = []
                    for k, v in value.items():
                        if isinstance(v, list):
                            for entry in v:
                                new_list.append((k, entry))
                        else:
                            new_list.append((k, v))
                    self._to_xml(xml, new_list)
                    # xml.endElement(key)
                elif isinstance(value, OrderedDict) and key in ['field']:
                    tag_name = self._create_inner_tag_name(key)
                    self._to_xml(xml, value)
                elif isinstance(value, OrderedDict) and key in ['layout']:
                    tag_name = "fields"
                    modified_value = OrderedDict()
                    modified_value["fields"] = value['layout']
                    self._to_xml(xml, modified_value)
                elif isinstance(value, str) and tag_name in ["field", None]:
                    tag_name = None
                    self._to_xml(xml, value, tag_name=tag_name)
                else:
                    self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(smart_text(data))


class GeoJsonRenderer(renderers.BaseRenderer):
    media_type = 'application/json'
    format = 'geojson'

    def render(self, data, media_type=None, renderer_context=None):
        return smart_text(data)


class RDFBaseRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'rdf'

    def render(self, data, media_type=None, renderer_context=None):
        g = Graph(namespace_manager=get_namespace_manager())
        g.parse(data=data, format='n3')
        return smart_text(g.serialize(format=self.format))


class JSONLDRenderer(RDFBaseRenderer):
    media_type = 'application/json'
    format = 'json-ld'


class RDFRenderer(RDFBaseRenderer):
    media_type = 'application/rdf+xml'
    format = 'rdf'

    def render(self, data, media_type=None, renderer_context=None):
        g = Graph()
        g.namespace_manager = get_namespace_manager()
        g.parse(data=data, format='n3')
        return smart_text(g.serialize(format='xml'))


class NTRIPLESRenderer(RDFBaseRenderer):
    media_type = 'text/plain'
    format = 'nt'


class TURTLERenderer(RDFBaseRenderer):
    media_type = 'text/turtle'
    format = 'turtle'


class N3Renderer(renderers.BaseRenderer):
    media_type = 'text/n3'
    format = 'n3'

    def render(self, data, media_type=None, renderer_context=None):
        return smart_text(data)
