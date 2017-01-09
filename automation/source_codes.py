import json
from os import path

import unicodecsv
import xlrd
from xlrd.biffh import XLRDError

from django.db.models import Q

from django.conf import settings

from redirect.models import DestinationManipulation


def get_book(location):
    """
    Creates an xlrd Book from the provided location

    Inputs:
    :location: string or unicode path to a local file or a file-like object

    Outputs:
    :book: instance of xlrd.book.Book
    """
    if not isinstance(location, (unicode, str)):
        book = xlrd.open_workbook(file_contents=location.read())
    else:
        book = xlrd.open_workbook(location)
    setattr(book, 'source_code_sheet', book.sheets()[0])
    return book


def get_csv(location):
    if not isinstance(location, (unicode, str)):
        csv = unicodecsv.reader(location)
    else:
        csv = unicodecsv.reader(open(location))
    return csv


def get_values(sheet, source_name, view_source_column=2, source_code_column=1):
    """
    Parse source codes from an Excel worksheet, returning the result

    Inputs:
    :sheet: Excel worksheet that contains source codes
    :source_name: Parameter to use for all source codes (e.g. src for Taleo),
        Pass None if spreadsheet already contains the desired parameter
    :view_source_column: Column containing view sources; 0-based in xlrd,
        default: 2
    :source_code_column: Column containing source codes; 0-based in xlrd,
        default: 1

    Outputs:
        List of tuples: [(view_source_1, source_code), (view_source_2,...)]
    """
    view_sources = [vs.value for vs in sheet.col(view_source_column)]
    source_parts = [cell.value for cell in sheet.col(source_code_column)]

    # Finds and returns all blank entries in a list
    get_blanks = lambda list_: [index for index, element
                                in enumerate(list_)
                                if element == '']

    # Pops blank indices from the view_sources and source_parts lists
    pop_blanks = lambda blanks: [(view_sources.pop(blank),
                                  source_parts.pop(blank))
                                 for blank in blanks[::-1]]

    for list_ in [view_sources, source_parts]:
        pop_blanks(get_blanks(list_))

    # The first row is a header; skip it
    view_sources = view_sources[1:]
    source_parts = source_parts[1:]

    if isinstance(source_parts[0], float):
        source_parts = [int(part) for part in source_parts]

    # Make a list of cell indices that contain multiple view sources
    multiple_view_sources = [view_sources.index(vs)
                             for vs in view_sources
                             if isinstance(vs, (str, unicode)) and '/' in vs]

    for index in multiple_view_sources:
        # For each entry that contains multiple view sources, split it into
        # its components,
        split = view_sources[index].split('/')

        # replace the cell containing multiple view sources with one view source
        view_sources[index] = split.pop(0).strip()

        # append the remaining view sources to the end of the list
        # and duplicate the relevant source code for each
        for additional in split:
            view_sources.append(additional.strip())
            source_parts.append(source_parts[index])

    parsed_view_sources = []
    bad_view_sources = []
    seen = set()
    with open(path.join(settings.PROJ_ROOT,
                        'jsondata/view_source_conversion.json')) as f:
        # Grab our list of equivalent view sources
        conversion = json.load(f)
    conversion_lists = [[int(item) for item in list_]
                        for list_ in conversion.values()]
    for index, value in enumerate(view_sources):
        try:
            # Ensure all elements in the view source list are integers
            int_value = int(value)
        except ValueError:
            # The current element is not an integer; add it to the list of
            # elements to be removed
            bad_view_sources.append(index)
            continue
        parsed_view_sources.append(int_value)

    for index in bad_view_sources[::-1]:
        # Discard all source codes that correspond to a non-integer view source
        source_parts.pop(index)
    view_sources = parsed_view_sources

    for index, value in enumerate(view_sources[:]):
        # Keep track of the view sources we've seen thus far so we don't
        # double up on one.
        if value not in seen:
            seen.add(value)

            # Search for a list of view sources containing ours.
            for list_ in conversion_lists:
                if value in list_:
                    # Found a list of view sources. Add all of them to the seen
                    # set so we don't do this for each one.
                    seen.update(list_)

                    # Determine which view sources we're not adding so we can
                    # add them now.
                    # Example: list_ = {1,2,3}, view_sources=[1,2,4]
                    # list_.difference(view_sources) == {3}; we'll add view
                    # source 3 to our list.
                    to_add = set(list_).difference(view_sources)
                    view_sources.extend(to_add)
                    for _ in to_add:
                        source_parts.append(source_parts[index])
                    # view sources aren't duplicated between the lists; break
                    # so we don't do unnecessary work.
                    break
            # If we fell out of the loop, we didn't have to add anything.

    # Some files already contain query parameters; in those cases, we don't
    # need to do any additional handling.
    if source_name:
        if source_name[0] not in ['?', '&']:
            source_name = '?%s' % source_name
        if source_name[-1] != '=':
            source_name = '%s=' % source_name
    else:
        source_name = ''

    # Construct source codes from the parameter we were passed (if any)
    # and the values we parsed from the spreadsheet
    source_codes = ['%s%s' % (source_name, part) for part in source_parts]

    return zip(view_sources, source_codes)


def add_source_codes(buids, codes):
    """
    Adds the specified source codes to a list of buids. Does not handle the
    case where there are non-sourcecodetag manipulations for a given buid/vs

    Inputs:
    :buids: List of buids that we are going to add source codes to
    :codes: List of tuples returned by get_values

    Outputs:
    :stats: Dictionary describing what happened in this method; contains the
        number of added and modified source codes as well as the total
    """
    # Make source codes easy to look up by view source
    code_dict = {code[0]: code for code in codes}

    if not isinstance(buids, (list, set)):
        buids = [buids]
    # Pulling buids from the database returns integers; In order to do set
    # operations between the two, these need to be ints as well
    buids = [int(buid) for buid in buids]

    all_view_sources = [code[0] for code in codes]
    all_manipulations = set((buid, vs) for buid in buids
                            for vs in all_view_sources)
    existing = set(DestinationManipulation.objects.filter(
        buid__in=buids, view_source__in=all_view_sources,
        action='sourcecodetag').values_list('buid', 'view_source'))
    new = all_manipulations.difference(existing)

    stats = {
        'added': len(new),
        'modified': len(existing),
        'total': len(all_manipulations)
    }

    # Bulk create manipulations that don't exist yet
    new_list = []
    for new_info in new:
        manipulation_info = code_dict[new_info[1]]
        new_list.append(DestinationManipulation(
            action_type=1, buid=new_info[0], view_source=manipulation_info[0],
            action='sourcecodetag', value_1=manipulation_info[1]))
    DestinationManipulation.objects.bulk_create(new_list)

    for existing_info in existing:
        manipulation_info = code_dict[existing_info[1]]
        DestinationManipulation.objects.filter(
            buid=existing_info[0], view_source=manipulation_info[0],
            action='sourcecodetag').update(
                value_1=manipulation_info[1])

    return stats


def add_destination_manipulations(buids, codes):
    """
    Adds the provided manipulations to a list of buids.

    Inputs:
    :buids: List of buids that we're adding these manipulations to
    :codes: List of dictionaries produced by process_csv

    Outputs:
    :stats: Dictionary describing the results of this method call; contains the
        number of added and modified manipulations and the total count
    """
    # This differs from how add_source_codes handles things. I would like to
    # eventually refactor that method to do something similar but that's out
    # of scope for the current task. - TP
    code_dict = {(int(code['view_source']), int(code['action_type'])): code
                 for code in codes}

    # BUIDs are optional; if none are provided, pull them from the csv
    if not buids:
        buids = [code['buid'] for code in codes]
    elif not isinstance(buids, (list, set)):
        buids = [buids]
    buids = map(int, buids)

    vs_and_action_type = set((int(vs), int(action_type))
                             for (vs, action_type) in code_dict.keys())

    # Build up the list of possible matching manipulations. This will be used
    # to determine when to update an entry and when to create a new one.
    existing_options = Q()
    for item in vs_and_action_type:
        for buid in buids:
            existing_options |= Q(buid=buid, view_source=item[0],
                                  action_type=item[1])

    # At the end of this method, we should have this set of entries in the
    # DestinationManipulation table. This set, in conjunction with `existing`,
    # will be used to determine if we're adding or updating an entry.
    all_manipulations = set((buid, item[0], item[1]) for buid in buids
                            for item in vs_and_action_type)
    existing = set(DestinationManipulation.objects.filter(
        existing_options).values_list('buid', 'view_source', 'action_type'))

    new = all_manipulations.difference(existing)

    stats = {
        'added': len(new),
        'modified': len(existing),
        'total': len(all_manipulations)
    }

    new_list = []
    for new_info in new:
        manipulation_info = code_dict[(new_info[1], new_info[2])]
        manipulation_info['buid'] = new_info[0]
        new_list.append(DestinationManipulation(**manipulation_info))
    DestinationManipulation.objects.bulk_create(new_list)

    for existing_info in existing:
        manipulation_info = code_dict[(existing_info[1], existing_info[2])]
        manipulation_info['buid'] = existing_info[0]
        DestinationManipulation.objects.filter(
            buid=existing_info[0], view_source=existing_info[1],
            action_type=existing_info[2]).update(**manipulation_info)

    return stats


def process_spreadsheet(location, buids, source_name, view_source_column=2,
                        source_code_column=1, add_codes=True):
    """
    Chains get_book and get_values, optionally executes add_source_codes

    Inputs:
    :location: Location of Excel spreadsheet, either as a string or in memory
    :buids: List of business units
    :source_name: Parameter name to use for source codes
    :view_source_column: Column of worksheet that contains view sources
    :source_code_column: Column of worksheet that contains source codes
    :add_codes: Boolean denoting whether we should add source codes;
        Default: True

    Outputs:
        If add_codes==True, returns summary of operations
        Else, returns source codes to be added
    """
    book = get_book(location)
    codes = get_values(book.source_code_sheet, source_name, view_source_column,
                       source_code_column)
    if add_codes:
        return add_source_codes(buids, codes)
    else:
        return codes


def process_csv(location, buids, add_codes=True):
    """
    Grabs a csv file by name or file handle, extracts manipulation
    values, and optionally adds them to the database.

    Inputs:
    :location: Location of csv file, as a string or file handle
    :buids: List of business units
    :add_codes: Boolean denoting whether we should add these manipulations;
        Default: True

    Outputs:
    Summary of operations if add_codes==True
    Manipulations to be added if add_codes==False
    """
    csv = get_csv(location)
    header = csv.next()

    # The csvs exported from our Django admin include human-readable column
    # names. We want the actual columns.
    expected_header = [u'BUID', u'View Source', u'View Source Name',
                       u'Action Type', u'Action', u'Value 1', u'Value 2']
    # This file should have come from an export. If the headers are off,
    # other elements may be incorrect. Fail early.
    assert header == expected_header, ('Header mismatch: csv has "%s", '
                                       'expected "%s"') % (
        ",".join(set(header).difference(expected_header)),
        ",".join(set(expected_header).difference(header)))
    fields = ['buid', 'view_source', 'view_source_name', 'action_type',
              'action', 'value_1', 'value_2']
    codes = [dict(zip(fields, code)) for code in csv]
    for code in codes:
        code['view_source'] = int(code['view_source'])
        del code['view_source_name']

    seen = set()
    with open(path.join(settings.PROJ_ROOT,
                        'jsondata/view_source_conversion.json')) as f:
        conversion = json.load(f)
    conversion_lists = [[int(item) for item in list_]
                        for list_ in conversion.values()]
    all_view_sources = {code['view_source'] for code in codes}
    for index, value in enumerate(codes[:]):
        vs = value['view_source']
        if vs not in seen:
            seen.add(vs)

            for list_ in conversion_lists:
                if vs in list_:
                    seen.update(list_)

                    to_add = set(list_).difference(all_view_sources)
                    for item in to_add:
                        new_dict = value.copy()
                        new_dict['view_source'] = item
                        codes.append(new_dict)
                    break

    if add_codes:
        return add_destination_manipulations(buids, codes)
    else:
        return codes


def process_file(location, buids, source_name, view_source_column=2,
                 source_code_column=1, add_codes=True):
    """
    Naively determines if the file we've been given is a spreadsheet or csv.
    """
    try:
        return process_spreadsheet(location, buids, source_name,
                                   view_source_column, source_code_column,
                                   add_codes)
    except XLRDError:
        # If we had a filename, this would be easy. As we may have a filename
        # or a file handle, it's easier to just try as Excel and then try as
        # csv if that fails.
        return process_csv(location, buids, add_codes)
