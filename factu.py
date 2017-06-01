
import sys
from datetime import date, datetime
import csv
from pathlib import Path
from shutil import move


KEYS = [
    'Job Index ',
    'Protocol',
    ' User Name',
    ' Host Name',
    ' File Name',
    ' Job Name',
    ' Pages(Sheets) Printed',
    ' Pages(Sides) Printed',
    ' Start Time',
    ' End Time',
    ' Interpreter Duration',
    ' Paper Type',
    ' Custom Name',
    ' Paper Size',
    ' Standard Capacity Cyan Used',
    ' Standard Capacity Magenta Used',
    ' Standard Capacity Yellow Used',
    ' Standard Capacity Black Used',
    ' High Capacity Cyan Used',
    ' High Capacity Magenta Used',
    ' High Capacity Yellow Used',
    ' High Capacity Black Used',
    'Printer Model Number',
]

PRIX_COULEUR = 389 / 100
PRIX_NOIR = 396 / 100
PRIX_FUSER = 242 / 80000
PRIX_IMAGEUR = 171 * 4 / 80000
PRIX_PAPIER_A3 = 77 / 2500
PRIX_PAPIER_A4 = 42 / 2500
SOPHIE_PRICE_FACTOR = 1.1

stylesheet = """
body {
  width:70%;
  margin: auto;
  font-family: monospace;
}

h1 {
  color: #4286f4;
  font-size: 200%
}

.date {
    color:brown;
}

.price{
        font-size: 200%;
}

.pphn .hostname {
        color: cadetblue;
    font-family: monospace;
}

.pphn .price{
        font-size: 150%;
}

table {
	color:#666;
	font-size:12px;
	text-shadow: 1px 1px 0px #fff;
	background:#eaebec;

}
table th {
	padding:12px 12px 12px 12px;

	background: #ededed;
}
table th:first-child {
	text-align: left;
	padding-left:20px;
}
table tr:first-
table tr {
	text-align: center;
	padding-left:20px;
}
table td:first-child {
	text-align: left;
	padding-left:20px;
	border-left: 0;
}
table td {
	padding:8px;
	background: #fafafa;
}
table tr.even td {
	background: #f6f6f6;
	background: -webkit-gradient(linear, left top, left bottom, from(#f8f8f8), to(#f6f6f6));
	background: -moz-linear-gradient(top,  #f8f8f8,  #f6f6f6);
}
table tr:last-child td {
	border-bottom:0;
}
table tr:hover td {
	background: #f2f2f2;
	background: -webkit-gradient(linear, left top, left bottom, from(#f2f2f2), to(#f0f0f0));
	background: -moz-linear-gradient(top,  #f2f2f2,  #f0f0f0);
}
"""

template_factu = """
<html>
<head>
<title>facture xerox</title>
<style>
{style}
</style>
</head>
<body>
<section>
<h1>{user}</h1>
<div class="date">date: {date}</div>
<div class="price">prix: {total_price:.2f} euros</div>
</section>
<section>
<h1>Prix par hostname</h1>
{pphn}
</section>
<section>
<h1>jobs</h1>
<div>
<em>extrait de <a href="{reference_csv}">{reference_csv}</a></em>
</div>
<table>
<thead>
      <th>date</th>
      <th>protocol</th>
      <th>hostname</th>
      <th>fichier</th>
      <th>format</th>
      <th>nombre de pages</th>
      <th>nombre de feuilles</th>
      <th>prix</th>
    </tr>
  </thead>
<tbody>
{jobs}
</tbody>
</table>
</section>
</body>
</html>
"""

template_print = """
<tr>
<td>{start_time}</td>
<td>{protocol}</td>
<td>{hostname}</td>
<td>{filename}</td>
<td>{size}</td>
<td>{pages}</td>
<td>{sheets}</td>
<td>{price:.2f}</td>
</tr>
"""

template_index = """
<html>
<head>
<title>xerox - index</title>
<style>
{style}
</style>
</head>
<body>
{items}
</body>
</html>
"""

template_index_item = """
<section>
<h1><a href="{user}.html">{user}</h1>
</section>
"""

template_pphn = """
<div class="pphn">
<span class="hostname">{hostname}</span>
<span class="price">{price:.2f}</span>
</div>
"""


def price_per_hostname(jobs):
    pphn = dict()
    for job in jobs:
        hn = job['hostname']
        if hn not in pphn:
            pphn[hn] = dict(hostname=hn, price=0)
        pphn[hn]['price'] += job['price']

    lines = []
    for hn in pphn:
        lines.append(template_pphn.format(**pphn[hn]))

    return ''.join(lines)


def emit(path, user, total_price, jobs, reference_csv):
    job_lines = []
    for job in jobs:
        job_lines.append(template_print.format(**job))
    rows = ''.join(job_lines)

    html = template_factu.format(
        pphn=price_per_hostname(jobs),
        user=user,
        total_price=total_price,
        jobs=rows,
        date=datetime.now().isoformat(),
        style=stylesheet,
        reference_csv=reference_csv
    )
    with path.open('w') as out:
        out.write(html)


def get_total(jobs):
    t = 0
    for job in jobs:
        t += job['price']
    return t


def make_jobs(current_path):
    db = dict()
    with current_path.open('r') as current:
        current_reader = csv.DictReader(current)
        for row in current_reader:
            user = row[KEYS[2]].lstrip().rstrip()
            hostname = row[KEYS[3]]
            filename = row[KEYS[4]]
            start_time = row[KEYS[8]]
            pages = int(row[KEYS[7]])
            size = row[KEYS[13]]
            sheets = int(row[KEYS[6]])
            protocol = row[KEYS[1]]

            cyan = float(row[KEYS[18]][:-1])
            magenta = float(row[KEYS[19]][:-1])
            yellow = float(row[KEYS[20]][:-1])
            black = float(row[KEYS[21]][:-1])

# COUT_PAPIER = k11 == ' A3' ? PRIX_PAPIER_A3 * k6 :  PRIX_PAPIER_A4 * k6
# SUM([k18:k20] * PRIX_COULEUR , k21 * PRIX_NOIR, K7 * P_F, k7 * P_I,
# COUT_PAPIER)

            # print('{} {}'.format(cyan, row[KEYS[18]]))
            max_color_price = 1.5
            paper_price = 0

            if ' A4' == size:
                paper_price = sheets * PRIX_PAPIER_A4
                max_color_price = max_color_price / 2
            else:
                paper_price = sheets * PRIX_PAPIER_A3

            price = (
                min(max_color_price * pages, cyan * PRIX_COULEUR)
                + min(max_color_price * pages, magenta * PRIX_COULEUR)
                + min(max_color_price * pages, yellow * PRIX_COULEUR)
                + min(max_color_price * pages, black * PRIX_NOIR)
                + (pages * PRIX_FUSER)
                + (pages * PRIX_IMAGEUR)
                + paper_price
            ) * SOPHIE_PRICE_FACTOR

            # print('{} = {} {} {} {} {} {} {}'.format(
            #     price, cyan, (magenta * PRIX_COULEUR), (yellow * PRIX_COULEUR), (
            #         black * PRIX_NOIR), (pages * PRIX_FUSER), (pages * PRIX_IMAGEUR), paper_price
            # ))

            if user not in db:
                db[user] = []

            db[user].append(dict(
                user=user,
                filename=filename,
                start_time=start_time,
                pages=pages,
                size=size,
                sheets=sheets,
                price=price,
                hostname=hostname,
                protocol=protocol
            ))

    return db


COMMANDS = ['update', 'close']


def main():
    today = date.today().isoformat()
    command = sys.argv[1]
    if command not in COMMANDS:
        print(
            'command must be one of {}, yours was {}'.format(COMMANDS, command))
        sys.exit(1)
    current_path = Path(sys.argv[2])
    base_dir = Path(sys.argv[3])

    out_dir = None
    reference_csv = None
    if 'update' == command:
        out_dir = base_dir
        reference_csv = current_path
    else:
        out_dir = base_dir.joinpath(today)
        reference_csv = out_dir.joinpath('current-{}.csv'.format(today))

    if out_dir.exists() == False:
        out_dir.mkdir(parents=True)

    db = make_jobs(current_path)

    if 'close' == command:
        for user in db:
            jobs = db[user]

            emit(
                out_dir.joinpath('{}-{}.html'.format(user, today)),
                user,
                get_total(jobs),
                jobs,
                reference_csv.name
            )

        move(current_path.as_posix(), reference_csv.as_posix())

    else:
        index_items = []
        for user in db:
            jobs = db[user]
            emit(
                out_dir.joinpath('{}.html'.format(user)),
                user,
                get_total(jobs),
                jobs,
                reference_csv.name
            )
            index_items.append(template_index_item.format(user=user))

        index = template_index.format(
            items=''.join(index_items), style=stylesheet)
        with out_dir.joinpath('index.html').open('w') as index_file:
            index_file.write(index)


if __name__ == '__main__':
    main()
