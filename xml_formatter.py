__author__ = 'pfischi'

from lxml import etree


class NamedXmlElements():
    exception = 'exception'
    speaker = 'speaker'
    info = 'info'
    data = 'data'


def xml_format_status(status, info='', device_properties={}):
    root = etree.Element('result', type=NamedXmlElements.data, status=str(status))

    data_element = etree.SubElement(root, NamedXmlElements.data)

    for k, v in device_properties.items():
        element = etree.SubElement(data_element, k)
        element.text = str(v)

    info_element = etree.SubElement(root, NamedXmlElements.info)
    info_element.text = str(info)

    tree = etree.ElementTree(root)
    return etree.tostring(tree, pretty_print=True)


def xml_format_speaker_data(speakers, status=True, info=''):
    root = etree.Element('result', type=NamedXmlElements.data, status=str(status))

    data_element = etree.SubElement(root, NamedXmlElements.data)

    for speaker in speakers:

        speaker_element = etree.SubElement(data_element, NamedXmlElements.speaker)

        for property in dir(speaker):
            info_element = etree.SubElement(speaker_element, property)
            info_element.text = str(getattr(speaker, property))

    info_element = etree.SubElement(root, NamedXmlElements.info)
    info_element.text = str(info)

    tree = etree.ElementTree(root)

    return etree.tostring(tree, pretty_print=True)


def xml_format_exception(exception, info=''):
    root = etree.Element('result', type=NamedXmlElements.exception)

    exception_element = etree.SubElement(root, NamedXmlElements.exception)
    exception_element.text = str(exception)

    info_element = etree.SubElement(root, NamedXmlElements.info)
    info_element.text = str(info)

    tree = etree.ElementTree(root)
    return etree.tostring(tree, pretty_print=True)
