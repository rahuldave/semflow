"""
This is to be used by mast_proprdf.py and determines how to parse
a line from the <mission>_proposal.txt file, since it appears to be
mission specific.

FUSE proposals look like:

A061|1| |JOHN|HUTCHINGS|Dominion Astrophysical Observatory, HIA, NRC of Canada, Cana|We propose FUSE observations of the brightest OB stars in the local group galaxies M31 and M33.  The stars are faint but their UV fluxes are known from HST and UIT data.  This will extend the stellar wind and interstellar studies currently under way with HST and ground-based telescopes, with similar resolution (1000) and S/N.  The program will expand our comparison of stellar winds, evolution, and the ISM among the major galaxies of the local group.

Z908|0| | |Andersson|FUSE Observatory Program|This program will obtain emission line spectra from 4 positions in the Vela SNR.
Z008|0| |Dr. Peter|Lundqvist|Stockholm Observatory|O VI emission from SN 1987A in the Large Magellanic Cloud will be observed to characterize the time dependence of the hot gas. The observation will be done on the LWRS aperture to obtain the total O VI flux from the SN environment.

So there's several issues with the PI name fields:

  - may be all upper case
  - may start with an honorific

At present we strip out the honorific but do not do try and fix the
case.

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

    (propid, ignore, title, pi_first, pi_last, place, remainder) = \
        line.split("|", 6)

    # strip out honorifics from the first name
    for h in ["Mr. ", "Dr. ", "Prof. "]:
        if pi_first.startswith(h):
            pi_first = pi_first[len(h):]
            break
        
    # Could try and do case normalization here too
    #if pi_first.strip() != "":
    #    print("#First: [{0}]".format(pi_first))
    #if pi_last.strip() != "":
    #    print("#Last: [{0}]".format(pi_last))
    
    out = { "propid": propid }

    def addit(field, value):
        val = value.strip()
        if val != "":
            out[field] = val

    addit("title", title)
    addit("pi_first", pi_first)
    addit("pi_last", pi_last)

    # looks like no titles for FUSE proposals
    #if title.strip() != "":
    #    print("DBG: propid={0} title={1}".format(propid, title))
        
    return out
