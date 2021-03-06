# -*- coding: utf-8 -*-

import queries

from django.http import Http404
from django.template import RequestContext
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_list_or_404

from .models import MailingList, Thread


def thread(request, mailinglist, thread_token):

    try:
        first_message = queries.get_first_message_in_thread(mailinglist, 
                                                            thread_token)
    except ObjectDoesNotExist:
        raise Http404
    order_by = request.GET.get('order')
    if order_by == 'voted':
        msgs_query = queries.get_messages_by_voted()
    else:
        msgs_query = queries.get_messages_by_date()

    msgs_query = msgs_query.filter(thread__subject_token=thread_token)
    msgs_query = msgs_query.filter(thread__mailinglist__name=mailinglist)
    emails = msgs_query.exclude(id=first_message.id)

    total_votes = first_message.votes_count()
    for email in emails:
        total_votes += email.votes_count()

    # Update relevance score
    query = Thread.objects.filter(mailinglist__name=mailinglist)
    thread = query.get(subject_token=thread_token)
    thread.update_score()

    template_data = {
        'first_msg': first_message,
        'emails': [first_message] + list(emails),
        'pagehits': queries.get_page_hits(request.path_info),
        'total_votes': total_votes,
    }

    return render(request, 'message-thread.html', template_data)


def list_messages(request):

    selected_list = request.GET.get('list')

    order_by = request.GET.get('order')
    if order_by == 'hottest':
        threads = queries.get_hottest_threads()
    else:
        threads = queries.get_latest_threads()

    mail_list = request.GET.get('list')
    if mail_list:
        threads = threads.filter(mailinglist__name=mail_list)

    paginator = Paginator(threads, 16)
    try:
        page = int(request.GET.get('p', '1'))
    except ValueError:
        page = 1
    threads = paginator.page(page)

    lists = MailingList.objects.all()

    template_data = {
        'lists': lists,
        'n_results': paginator.count,
        'threads': threads,
        'selected_list': selected_list,
        'order_by': order_by,
    }
    return render(request, 'message-list.html', template_data)
