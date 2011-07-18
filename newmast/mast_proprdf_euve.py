"""
This is to be used by mast_proprdf.py and determines how to parse
a line from the <mission>_proposal.txt file, since it appears to be
mission specific.

EUVE proposals are as IUE but without the last |N field:

99-036|A Deep EUVE Variability Study of the Seyfert Galaxy NGC 4051| Antonella|Fruscione|Harvard CfA/CXC|The Seyfert galaxy NGC~4051 is one of the brightest AGN in the EUV and X-ray sky. It is also one of the most rapidly variable. It is therefore an excellent candidate on which to study the origin of the EUV and X-ray emission in AGN. Its central black hole mass is quite small (approx 10e6 solar masses), making comparison with the behaviour of galactic black hole X-ray binary systems (BHXRBs) much easier than with other AGN with more massive black holes where characteristic variability timescales will be longer. Comptonisation of soft photons is a widely favoured possibility for the production of the X-ray/EUV emission in AGN. Here we propose to build on previous very successful coordinated EUVE and RXTE observations to further test the Comptonisation model and to investigate the similarities between AGN and BHXRBs. We propose to carry out a continuous 1 month EUVE observation to be coordinated with a 2 month RXTE programme of 4-times daily observations.

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
    addit("pi_first", pi_first)
    addit("pi_last", pi_last)

    return out

