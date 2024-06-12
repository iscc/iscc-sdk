"""Monkey Patches"""

import ebookmeta
from ebookmeta import Epub2, _get_ebook


def set_author_list(self, author_list):  # pragma: no cover
    """Don´t set role on creator"""
    node_list = self._get_all('opf:metadata/dc:creator[@opf:role="aut" or not(@opf:role)]')
    for node in node_list:
        node.getparent().remove(node)
    meta_node = self._get("opf:metadata")
    for author in author_list:
        if author:
            node = self._sub_element(meta_node, "dc:creator")
            node.text = author


Epub2.set_author_list = set_author_list


def set_description(self, description):  # pragma: no cover
    node = self._get("opf:metadata/dc:description")
    if node is None:
        meta_node = self._get("opf:metadata")
        node = self._sub_element(meta_node, "dc:description")
    node.text = description


Epub2.set_description = set_description


def set_metadata(file, meta):  # pragma: no cover
    ebook = _get_ebook(file)

    ebook.set_title(meta.title)
    ebook.set_description(meta.description)
    ebook.set_author_list(meta.author_list)
    ebook.set_series(meta.series)
    ebook.set_series_index(meta.series_index)
    ebook.set_lang(meta.lang)
    ebook.set_tag_list(meta.tag_list)
    ebook.set_translator_list(meta.translator_list)
    ebook.set_cover_data(meta.cover_file_name, meta.cover_media_type, meta.cover_image_data)

    # Set publish info for FB2
    if meta.format == "fb2":
        ebook.set_publish_title(meta.publish_info.title)
        ebook.set_publish_publisher(meta.publish_info.publisher)
        ebook.set_publish_city(meta.publish_info.city)
        ebook.set_publish_year(meta.publish_info.year)
        ebook.set_publish_series(meta.publish_info.series)
        ebook.set_publish_series_index(meta.publish_info.series_index)
        ebook.set_publish_isbn(meta.publish_info.isbn)

    ebook.save()


ebookmeta.set_metadata = set_metadata
