"""

Read in pipe-separated obscore data from MAST.

We assume the data is in pipe-separated format and has no header
line. The format is taken to be (from initial obscore tables in CSV
format):

% head -1 obscore.csv | tr , '\n' | cat -n
     1  s_ra
     2  s_dec
     3  datalen
     4  radecsys
     5  equinox
     6  timesys
     7  specsys
     8  vover
     9  vodate
    10  target_name
    11  ra_targ
    12  dec_targ
    13  title
    14  obs_creator_name
    15  obs_collection
    16  obs_publisher_did
    17  obs_id
    18  creation_date
    19  version
    20  instrument
    21  dssource
    22  em_domain
    23  der_snr
    24  spec_val
    25  spec_bw
    26  spec_fil
    27  em_res_power
    28  date_obs
    29  t_exptime
    30  t_min
    31  t_max
    32  aperture
    33  telescope_name
    34  tmid
    35  fluxavg
    36  fluxmax2
    37  em_min
    38  em_max
    39  min_flux
    40  max_flux
    41  min_error
    42  max_error
    43  access_format
    44  access_url
    45  representative
    46  preview
    47  project
    48  spectralaxisname
    49  fluxaxisname
    50  spectralsi
    51  fluxsi
    52  spectralunit
    53  fluxunit
    54  fluxucd
    55  fluxcal
    56  coord_obs
    57  coord_targ
    58  s_ra_min
    59  s_ra_max
    60  s_dec_min
    61  s_dec_max
    62  s_resolution
    63  t_resolution
    64  s_region
    65  o_fluxucd
    66  calib_level
    67  dataproduct_type
    68  t_span
    69  s_fov
    70  filesize
    71  access_estsize

"""

import sys 

import csv

__all__ = ('open_obscore', 'row2dict', 'get_column', 'check_row')

# A dialect for pipe-separated values
class PSV(csv.Dialect):
    """Pipe-separated values (separator is |).

    At present all we really care about is the delimiter
    and lineterminator fields; the others are guesses.
    """
    
    delimiter = '|'
    doublequote = False
    escapechar = '\\'
    lineterminator = "\r\n"
    quotechar = None
    quoting = csv.QUOTE_NONE
    skipinitialspace = True # not sure about this one
    
csv.register_dialect("psv", PSV)

"""
From

head -1 obscore.csv | tr , '\n' | awk '{ printf "  \"%s\",\n", $1 }' -

"""

_colnames = [
  "s_ra",
  "s_dec",
  "datalen",
  "radecsys",
  "equinox",
  "timesys",
  "specsys",
  "vover",
  "vodate",
  "target_name",
  "ra_targ",
  "dec_targ",
  "title",
  "obs_creator_name",
  "obs_collection",
  "obs_publisher_did",
  "obs_id",
  "creation_date",
  "version",
  "instrument",
  "dssource",
  "em_domain",
  "der_snr",
  "spec_val",
  "spec_bw",
  "spec_fil",
  "em_res_power",
  "date_obs",
  "t_exptime",
  "t_min",
  "t_max",
  "aperture",
  "telescope_name",
  "tmid",
  "fluxavg",
  "fluxmax2",
  "em_min",
  "em_max",
  "min_flux",
  "max_flux",
  "min_error",
  "max_error",
  "access_format",
  "access_url",
  "representative",
  "preview",
  "project",
  "spectralaxisname",
  "fluxaxisname",
  "spectralsi",
  "fluxsi",
  "spectralunit",
  "fluxunit",
  "fluxucd",
  "fluxcal",
  "coord_obs",
  "coord_targ",
  "s_ra_min",
  "s_ra_max",
  "s_dec_min",
  "s_dec_max",
  "s_resolution",
  "t_resolution",
  "s_region",
  "o_fluxucd",
  "calib_level",
  "dataproduct_type",
  "t_span",
  "s_fov",
  "filesize",
  "access_estsize",
]

_ncols = len(_colnames)
_colmap = dict(zip(_colnames, range(0,_ncols)))

def check_row(row):
    """Ensure the number of columns is correct.

    We could also check other items but for now do not
    bother.
    """
    
    if len(row) != _ncols:
        raise ValueError("Row contains {0} columns, expected {1}!\n\n{2}\n".format(len(row), _ncols, row))

def get_column(row, cname):
    """Return the cell for the given column name from the row,
    which is expected to be the return value of a csv reader
    object.

    We assume that check_row() has already been called on this
    row.
    """

    try:
        return row[_colmap[cname]]

    except KeyError:
        raise ValueError("Invalid column name: {0}!".format(cname))

def row2dict(row):
    "Return a dictionary of key=column-name, value=column-value."

    check_row(row)
    return dict(zip(_colnames, row))

def open_obscore(fname):
    """Open the input file, returning the
    CSV reader instance and file handle. This can be used

      (rdr, fh) = open_obscore('obscore.psv')
      for row in rdr:
          obsid = get_column(row, 'obs_id')
          ...

      fh.close()

    """
    
    fh = open(fname, "r")
    rdr = csv.reader(fh, dialect="psv")
    return (rdr, fh)

    
