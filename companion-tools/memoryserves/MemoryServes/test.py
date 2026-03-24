    def is_wanted_child(node, url):
        """
        Return whether the node has a child with following properties:
            type: text/x-moz-place
            uri: `url`
        """

        for child in node['children']:
            if child['type'] == 'text/x-moz-place':
                if child['uri'] == url:
                    return True
        return False

    def get_json_tags(bookmarks, url):
        """
        Iterates over *bookmarks* (dict) trying to find tags associated with the
        given *url*. Returns the tags found as a list.
        """

        if not bookmarks.has_key('root') or not bookmarks.has_key('children'):
            return []

        tag_titles = (item for item in bookmarks['children'] if item['title'] == 'Tags')
        children = (child for child in tag_titles
                    if child['type'] == 'text/x-moz-place-container')
        return [child['title'] for child in children if is_wanted_child(child, url)]