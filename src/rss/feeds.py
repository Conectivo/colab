#!/usr/bin/env python
# encoding: utf-8

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _

from super_archives.models import Thread
from super_archives import queries
from colab.deprecated import solrutils


class LatestThreadsFeeds(Feed):
    title = _(u'Latest Discussions')
    link = '/rss/threads/latest/'

    def items(self):
        return queries.get_latest_threads()[:20]

    def item_link(self, item):
        return item.latest_message.url

    def item_title(self, item):
        title = '[' + item.mailinglist.name + '] '
        title += item.latest_message.subject_clean  
        return title

    def item_description(self, item):
        return item.latest_message.body


class HottestThreadsFeeds(Feed):
    title = _(u'Discussions Most Relevance')
    link = '/rss/threads/hottest/'

    def items(self):
        return queries.get_hottest_threads()[:20]

    def item_link(self, item):
        return item.latest_message.url

    def item_title(self, item):
        title = '[' + item.mailinglist.name + '] '
        title += item.latest_message.subject_clean  
        return title  

    def item_description(self, item):
        return item.latest_message.body


class LatestColabFeeds(Feed):
    title = _(u'Latest collaborations')
    link = '/rss/colab/latest/'

    def items(self):
        items = solrutils.get_latest_collaborations(20)
        return items

    def item_title(self, item):
        type_ = item.get('Type') + ': '
        mailinglist = item.get('mailinglist')

        if mailinglist:
            prefix = type_ + mailinglist + ' - '
        else:
            prefix = type_

        return prefix + item.get('Title') 

    def item_description(self, item):
        return item.get('Description')

    def item_link(self, item):
        if item.get('Type') != 'thread':
            url = item.get('url')
        else:
            url = 'http://colab.interlegis.leg.br'
            url += item.get('url')
        return url

