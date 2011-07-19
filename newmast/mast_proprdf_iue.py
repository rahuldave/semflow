"""
This is to be used by mast_proprdf.py and determines how to parse
a line from the <mission>_proposal.txt file, since it appears to be
mission specific.

The IUE proposal list looks like

OD89K|Observing the Earth|Ralph C.|Bohlin|STScI|Abstract unavailable|N

where the 'Abstract unavailable' can be filled in with the abstract
text and this text can contain | characters. Note that the proposal
title can contain \n (at least it does for proposal id OD88Z).

The PI name can be first=" ", last="misc", which we treat as missing.
"""

def splitProposalLine(line):
    """Given a single line of text representing a proposal,
    split out the interesting fields and return as a dictionary:

      propid
      title
      pi_first
      pi_last

   The only required field is propid, although expect to have pi_last
   if pi_first is present.

   """

    (propid, title, pi_first, pi_last, place, remainder) = \
        line.split("|", 5)

    out = { "propid": propid }

    def addit(field, value):
        val = value.strip()
        if val != "":
            out[field] = val

    addit("title", title)

    # remove the misc PI field; it looks like all occurrences
    # have misc as a last name
    if pi_last != "misc":
        addit("pi_first", pi_first)
        addit("pi_last", pi_last)

    return out

