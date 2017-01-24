import json, math

from datetime import datetime, timedelta

from pymongoenv import connect_db

from django.shortcuts import HttpResponse
from django.http import HttpResponseNotAllowed, Http404
from django.views.decorators.csrf import csrf_exempt

from universal.api_validation import ApiValidator

from dateutil import parser as dateparser

from myjobs.decorators import requires
from universal.helpers import get_company_or_404
from myreports.models import (
    ReportingType, ReportType, DataType,
    ReportTypeDataTypes)


@requires("view analytics")
def views_last_7_days(request):
    """
    retrieve job views in last 7 days, return as json

    :param request:
    :return: dump of data

    """
    def format_dict(input_dict):
        record_date = input_dict['_id']
        return {
            'day': "%s/%s/%s" % (record_date['year'],
                                 record_date['month'],
                                 record_date['day']),
            'hits': input_dict['count']
        }

    job_views = get_mongo_db().job_views

    query = [
        {'$match': {'time_first_viewed': {'$type': 'date'}}},
        {'$match': {'time_first_viewed': {'$gte': datetime.today() -
                                                  timedelta(days=7)}}},
        {'$match': {'time_first_viewed': {'$lte': datetime.today()}}},
        {
            "$group":
                {
                    "_id":
                        {
                            "month": {"$month": "$time_first_viewed"},
                            "day": {"$dayOfMonth": "$time_first_viewed"},
                            "year": {"$year": "$time_first_viewed"}
                        },
                    "count": {"$sum": '$view_count'}
                }
        },
        {'$sort': {'_id': 1}}
    ]

    records = job_views.aggregate(query)

    return HttpResponse(json.dumps([format_dict(r) for r in records]))


@requires("view analytics")
def activity_last_7_days(request):
    """
    retrieve analytics hits in last 7 days, return as json

    :param request:
    :return: dump of data

    """
    def format_dict(input_dict):
        record_date = input_dict['_id']
        return {
            'day': "%s/%s/%s" % (record_date['year'],
                                 record_date['month'],
                                 record_date['day']),
            'hits': input_dict['count']
        }

    filtered_analytics = get_mongo_db().analytics

    query = [
        {'$match': {'time': {'$type': 'date'}}},
        {'$match': {'time': {'$gte': datetime.today() -
                                     timedelta(days=7)}}},
        {'$match': {'time': {'$lte': datetime.today()}}},
        {
            "$group":
                {
                    "_id":
                        {
                            "month": {"$month": "$time"},
                            "day": {"$dayOfMonth": "$time"},
                            "year": {"$year": "$time"}
                        },
                    "count": {"$sum": 1}
                }
        },
        {'$sort': {'_id': 1}}
    ]

    records = filtered_analytics.aggregate(query)

    return HttpResponse(json.dumps([format_dict(r) for r in records]))


@requires("view analytics")
def campaign_percentages(request):
    """
    retrieve campaign percentages, return as json

    :param request:
    :return: dump of data

    """
    def format_dict(input_dict):
        record_date = input_dict['_id']
        return input_dict

    filtered_analytics = get_mongo_db().analytics

    query = [
        {'$match': {'dn': {'$type': 'string'}}},
        {
            "$group":
                {
                    "_id":
                        {
                            "campaign": '$dn',
                        },
                    "count": {"$sum": 1}
                }
        },
        {'$limit': 10},
        {'$sort': {'_id': 1}}
    ]

    records = filtered_analytics.aggregate(query)

    return HttpResponse(json.dumps([format_dict(r) for r in records]))


def format_return_dict(record, group_label):
    """
    format return dict to have meaningful group by title rather than _id
    could be expanded to include other formatting as needed

    :param record: individual document retrieved from mongo
    :param group_label: the current group by column
    :return: formatted record


    """
    group_value = record.pop('_id')
    return_dict = {group_label: group_value}
    return_dict.update(record)
    return return_dict


def calculate_error_and_count(population, sample_count, row_count):
    """
    take a set of inputs and calculate the standard error and total count
    for a given row

    :param population: total number of rows matching top query
    :param sample_count: number of rows we are sampling
    :param row_count: the count for a given row
    :return: standard error and population-adjusted count (tuple)


    """
    proportion = float(row_count) / float(sample_count)
    inner = proportion * (1.0-proportion) / sample_count
    error = 3 * math.sqrt(inner) * population
    adjusted_count = population * proportion
    return error, int(adjusted_count)


def adjust_records_for_sampling(records, error_and_count):
    """
    adjust the records in the incoming data set to account for sample size vs
    population

    :param records: grouped records from mongo
    :param error_and_count: function to retrieve standard error and true count
    :return: records adjusted for


    """
    return_list = []
    for record in records:
        new_record = {}
        for key, value in record.iteritems():
            if key == '_id':
                new_record[key] = value
            else:
                new_record[key] = error_and_count(value)[1]
        return_list.append(new_record)

    return return_list


def build_top_query(date_start, date_end, buids=None):
    """
    build the highest level query from the data provided

    :param input_data: data from the request
    :param buids: BUIDs from the current company
    :return: top level query


    """

    top_query = {}
    if buids:
        if len(buids) > 1:
            buid_inner = {'$in': buids}
        else:
            buid_inner = buids[0]
        top_query = {'buid': buid_inner}

    top_query['time_first_viewed'] = {'$gte': date_start,
                                      '$lte': date_end
                                     }

    return top_query


def build_active_filter_query(query_data):
    """
    build active query filters based on what is provided

    :param query_data: query data from request
    :return: active filter queries


    """
    filter_match = {'$match': {}}
    for a_filter in query_data.get('active_filters', []):
        filter_match['$match'][a_filter['type']] = a_filter['value']

    return [filter_match] if filter_match['$match'] else []


def determine_data_group_by_and_remaining(query_data, reporttype_datatype):
    """
    determine what to group the data by. this can be retrieved from the db
    or provided in the request if a group_overwrite is present

    :param query_data: data from the request
    :return: the current group by and which remain


    """
    configuration = reporttype_datatype.configuration
    config_columns = configuration.configurationcolumn_set.all().order_by('order')
    active_filters = [f['type'] for f in query_data.get('active_filters', [])]
    remaining = config_columns.exclude(column_name__in=active_filters)
    group_overwrite = query_data.get('group_overwrite')
    if group_overwrite:
        overwrite = config_columns.get(column_name=group_overwrite)
        return overwrite, remaining.exclude(id=overwrite.id)
    elif remaining:
        return (remaining.first(),
                remaining.all().exclude(id=remaining.first().id))
    else:
        return None, None


def retrieve_sampling_query_and_count(collection, top_query, sample_size):
    """
    If the count from the top query is higher than the sample size, return
    a sampling pipeline component to place into the main query

    :param collection: the collection we're targeting (job_views typically)
    :param top_query: highest level filtering query
    :param sample_size: how large the sample should be (count cut off)
    :return: sample query (if needed) and count (tuple)


    """
    count = collection.find(top_query).count()
    sample_script = []
    if count > sample_size:
        sample_script = [{'$sample': {'size': sample_size}}]

    return sample_script, count


def build_group_by_query(group_by):
    """
    create group section of the aggregate query

    :param group_by: column by which to group data/get counts
    :return: group by query (list)


    """
    group_query = [
        {
            "$group":
                {
                    "_id": "$" + group_by,
                    "job_views": {"$sum": '$view_count'}
                }
            },
        {'$sort': {'job_views': -1}},
    ]

    return group_query


def get_mongo_db():
    """
    Retrieve the current mongo database (defined in settings.MONGO_DBNAME).

    :return: a mongo database

    """
    return connect_db().db


def get_company_buids(request):
    """
    retrieve a list of buids for a given company

    :param request:
    :return: buids (list)


    """
    user_company = get_company_or_404(request)
    job_sources = user_company.job_source_ids.all()
    return [job_source.id for job_source in job_sources]


def get_analytics_reporttype_datatype(analytics_report_id):
    """
    get analytics report type object based on an id provided

    :param analytics_report_id: id of desired report
    :return: report type or none
    """
    rit_analytics = ReportingType.objects.get(reporting_type="web-analytics")

    report_type = (
        ReportType.objects.active_for_reporting_type(rit_analytics)
        .filter(report_type=analytics_report_id))
    report_data = (
        ReportTypeDataTypes.objects.first_active_for_report_type_data_type(
            report_type=report_type,
            data_type=DataType.objects.filter(data_type='unaggregated')))

    return report_data


@requires("view analytics")
@csrf_exempt
def dynamic_chart(request):
    """
    return charting data given a set of filters, date range, and drilldown
    selection

    request
    {
        "date_start": "01/01/2016 00:00:00",
        "date_end": "01/08/2016 00:00:00",
        "active_filters": [{"type": "country", "value": "USA"},
                         {"type": "state", "value": "Indiana"}],
        "report": "found_on",
        "group_overwrite": "browser",
    }

    response
    {
        "column_names":
            [
                {"key": "browser", "label": "Browser"},
                {"key": "job_views", "label": "Job Views"},
             ],
        "rows":
            [
                {"browser": "Chrome", "job_views": "101",  "visits": "1050"},
                {"browser": "IE11", "job_views": "231", "visits": "841"},
                {"browser": "IE8", "job_views": "23", "visits": "341"},
                {"browser": "Firefox", "job_views": "21", "visits": "298"},
                {"browser": "Netscape Navigator", "job_views": "1", "visits": "1"},
                {"browser": "Dolphin", "job_views": "1", "visits": "1"}
             ]
    }


    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    validator = ApiValidator()

    query_data = json.loads(request.POST.get('request', '{}'))
    if not query_data:
        validator.note_error("No data provided.")

    if validator.has_errors():
        return validator.build_error_response()

    required_fields = ['date_end', 'date_start', 'report']
    for field in required_fields:
        if not query_data.get(field):
            validator.note_field_error(field, '%s is required' % field)

    if validator.has_errors():
        return validator.build_error_response()

    try:
        date_start = dateparser.parse(query_data['date_start'])
    except ValueError:
        validator.note_field_error('date_start',
                                   'Invalid date start: ' +
                                    query_data['date_end'])

    try:
        date_end = dateparser.parse(query_data['date_end'])
    except ValueError:
        validator.note_field_error('date_end',
                                   'Invalid date end: ' +
                                   query_data['date_end'])

    report_data = get_analytics_reporttype_datatype(query_data['report'])

    if not report_data:
        validator.note_field_error(
            "analytics_report_id", "No analytics report found.")

    if validator.has_errors():
        return validator.build_error_response()

    sample_size = 50000 # TODO: Add sample size to request object

    job_views = get_mongo_db().job_views

    buids = get_company_buids(request)

    top_query = build_top_query(date_start, date_end, buids)

    sample_query, total_count = retrieve_sampling_query_and_count(job_views,
                                                                  top_query,
                                                                  sample_size)

    if not sample_query:
        sample_size = total_count

    active_filter_query = build_active_filter_query(query_data)

    group_by, remaining_dimensions = determine_data_group_by_and_remaining(
        query_data, report_data
    )

    if not group_by:
        return HttpResponse(json.dumps({"rows": [],
                                        "column_names": [],
                                        "chart_type": None,
                                        "group_by": None,
                                        "remaining_dimensions": []
                                        }))

    group_query = build_group_by_query(group_by.column_name)

    query = [
        {'$match': top_query},
    ] + sample_query + active_filter_query + group_query

    records = job_views.aggregate(query, allowDiskUse=True)

    if sample_query:
        def curried_query(count):
            return calculate_error_and_count(total_count, sample_size, count)

        records = adjust_records_for_sampling(records, curried_query)

    response = {
        "column_names":
            [
                {"key": group_by.column_name,
                 "label": group_by.filter_interface_display},
                {"key": "job_views", "label": "Job Views"},
             ],
        "rows":
            [format_return_dict(r, group_by.column_name) for r in records],
        "chart_type": group_by.filter_interface_type,
        "group_by": group_by.column_name,
        "remaining_dimensions": [{"key": d.column_name,
                                  "label": d.filter_interface_display}
                                 for d in remaining_dimensions]
    }

    return HttpResponse(json.dumps(response))


@requires("view analytics")
def get_available_analytics(request):
    """Get a list of available analytics reports.

    {
        'reports': [
            {
                'value': 'job-locations',
                'display': 'Job Locations',
            },
            {
                'value': 'job-titles',
                'display': 'Job Titles',
            },
            {
                'value': 'job-found-on',
                'display': 'Site Found On',
            },
        ],
    }
    """
    # This and lines like it below should eventually be replaced by some kind
    # of general filter based on ReportingType and permissions.
    rit_analytics = ReportingType.objects.get(reporting_type="web-analytics")
    report_types = (
        ReportType.objects.active_for_reporting_type(rit_analytics)
        .order_by('description'))

    result = {
        'reports': [
            {
                'value': r.report_type,
                'display': r.description,
            }
            for r in report_types
        ],
    }

    return HttpResponse(json.dumps(result), content_type="application/json")

@requires("view analytics")
def get_report_info(request):
    """Get information about an analytics report.

    analytics_report_id: string id obtained from get_available_analytics
        under 'value'

    {
        'dimensions': [
            {
                'value': 'country',
                'display': 'Country',
                'interface_type': 'map:world',
            },
            {
                'value': 'title',
                'display': 'Job Title',
                'interface_type': 'string',
            },
            ...
        ]
    }
    """
    validator = ApiValidator()

    analytics_report_id = request.GET.get('analytics_report_id', '')
    if not analytics_report_id:
        validator.note_field_error(
            "analytics_report_id", "Value required.")

    if validator.has_errors():
        return validator.build_error_response()

    report_data = get_analytics_reporttype_datatype(analytics_report_id)

    if not report_data:
        validator.note_field_error(
            "analytics_report_id", "No analytics report found.")

    if validator.has_errors():
        return validator.build_error_response()

    config = report_data.configuration

    result = {
        'dimensions': [
            {
                'value': r.column_name,
                'display': r.filter_interface_display,
                'interface_type': r.filter_interface_type,
            }
            for r in config.configurationcolumn_set.all().order_by('order')
        ],
    }

    return HttpResponse(json.dumps(result), content_type="application/json")


def get_mongo_db():
    """
    Retrieve the current mongo database (defined in settings.MONGO_DBNAME).
    :return: a mongo database
    """
    return connect_db().db
