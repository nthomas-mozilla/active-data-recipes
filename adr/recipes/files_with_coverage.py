from __future__ import print_function, absolute_import

from collections import defaultdict

from ..cli import RecipeParser
from ..query import run_query

def run(args):
    parser = RecipeParser()
    parser.add_argument('--limit', required=False, default=10, type=int,
                        help="Total number of revisions to report (default: 10).")
    args = parser.parse_args(args)

    header = ['Revision', 'Files With Coverage', 'Total Files', 'Percent with Coverage']
    covered_files = next(run_query('covered_files'))['data']
    total_files = next(run_query('total_files'))['data']

    by_revision = {}
    by_date = {}
    for item in covered_files:
        # if we don't have 100 artifacts, something is broken, no data, or still ingesting
        if item[2] >= 100:
            # default total files=-1, in some cases this is reported
            by_revision[item[0]] = {'covered': item[3], 'total': -1}
            by_date[item[1]] = item[0]

    for item in total_files:
        if item[0] in by_revision:
            by_revision[item[0]]['total'] = item[2]

    data = []
    dates = sorted(by_date.keys(), reverse=True)

    for date in dates[0:args.limit]:
        rev = by_date[date]
        covered = by_revision[rev]['covered']
        total = by_revision[rev]['total']
        if covered < 0 or total < 0:
            continue
        data.append([rev, covered, total, round((float(covered) / total) * 100, 1)])
    data.insert(0, header)
    return data
