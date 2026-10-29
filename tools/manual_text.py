"""Texts taken from the Elektron Machinedrum manual (OS 1.63), Appendix A,
read from the online copy at manualsdir.com (the PDF itself is not reachable
from the build machine). Only machines whose text could be read are listed;
controls without an entry are shown with name and default only.
EFM and PI-RC/PI-CC (and TRX-SD) are still missing: fill in when available."""

FAMILY = {
    # (short synthesis name, manual sentence or None)
    "trx": ("classic analogue synthesis",
            'Manual: "TRX is inspired by classic analogue drum machine synthesis."'),
    "efm": ("Enhanced Feedback Modulation",
            "EFM = Enhanced Feedback Modulation, an FM-based MD-synth."),
    "pi": ("physical modelling",
           'Manual: "P-I is the physically informed MD-synth which simulates the behaviour of acoustic drums."'),
}

PTCH = "Controls the basic pitch of the drum."
DEC = "Controls the decay time."
HARD = "A higher value gives a harder strike."
TENS = "Regulates the effect of the high tension in the skin from a hard hit."
RING = "The drum's metallic ringing."
RVOL = "The volume of the snares' rattling."
RDEC = "The decay time of the rattling."

PARAMS = {
    "trxbd": dict(PTCH=PTCH, DEC=DEC, RAMP="Ramps the pitch.", RDEC="Speed of pitch ramp.",
                  STRT="Makes the start harder.", NOIS="Adds noise to the start of the sound.",
                  HARM="Adds extra harmonics.", CLIP="A special type of distortion."),
    "trxb2": dict(PTCH=PTCH, DEC=DEC, RAMP="Ramps the pitch.",
                  HOLD="Controls the initial hold time for the volume.",
                  TICK="Adds a tick to make the start harder.",
                  NOIS="Adds noise to the start of the sound.",
                  DIRT="Controls a bit reduction function for the bassdrum.",
                  DIST="A special type of distortion."),
    "trxxt": dict(PTCH=PTCH, DEC=DEC, RAMP="Ramps the pitch.", RDEC="Speed of pitch ramp.",
                  DAMP="Dampens the decay.", DIST="Distortion.", DTYP="Hardness of the distortion."),
    "trxxc": dict(PTCH=PTCH, DEC=DEC, RAMP="Ramps the pitch.", RDEC="Speed of the pitch ramp.",
                  DAMP="Dampens the decay part of the sound.", DIST="Distortion.",
                  DTYP="Hardness of the distortion."),
    "trxcp": dict(CLPY="Density of the clap.", TONE="Changes tonal quality.", HARD="Harder claps.",
                  RICH="Enhances the richness of the sound.", RATE="Rate of the individual claps.",
                  ROOM="Adds a room sound.", RSIZ="Changes the size of the room.",
                  RTUN="Changes the tonal quality of the room."),
    "trxrs": dict(PTCH="Controls the basic pitch.", DEC=DEC, DIST="Distortion."),
    "trxcb": dict(PTCH="Controls the basic pitch.", DEC=DEC, ENH="Enhances the body of the sound.",
                  DAMP="Dampens the decay part.", TONE="Changes tonal quality.",
                  BUMP="Adds a pitchshift at the start of the sound."),
    "trxch": dict(GAP="Changes the hi-hat gap.", DEC=DEC, HPF="High pass filters the sound.",
                  LPF="Low pass filters the sound.", MTAL="Adds extra metal character to the sound."),
    "trxcy": dict(RICH="Adds extra richness to the sound.", DEC=DEC,
                  TOP="Amount of high frequency harmonics.", TTUN="Tunes the top.",
                  SIZE="Changes the size of the cymbal.", PEAK="Gives the sound more edge."),
    "trxma": dict(ATT="Length of the attack.", SUS="Length of the sustain.",
                  REV="Reverses movement of the maracas.",
                  DAMP="Dampens the sound to make it more sparse.",
                  RATL="Adds extra rattle to the sound.", RTYP="Type of rattle.",
                  TONE="Changes tonal quality.", HARD="Gives the sound a harder character."),
    "trxcl": dict(PTCH="Controls the basic pitch.", DEC=DEC, DUAL="Introduces a dual attack.",
                  ENH="Enhances the tone.", TUNE="Detunes the sound.", CLIC="Adds a click at the start."),
    "pibd": dict(PTCH=PTCH, DEC=DEC, HARD=HARD, HAMR="A higher value gives a softer mallet.",
                 TENS=TENS, DAMP="Regulates the damping in the drum body."),
    "pisd": dict(PTCH=PTCH, DEC=DEC, HARD=HARD, TENS=TENS, RVOL=RVOL, RDEC=RDEC, RING=RING),
    "pimt": dict(PTCH=PTCH, DEC="Sets the decay time of the drum.", HARD=HARD,
                 HAMR="A higher value gives a softer mallet.", TUNE="Emulates different tuning of skins.",
                 DAMP="Regulates damping in the drum body.", SIZE="Regulates the size of the drum body.",
                 POS="Moves the striking point from the center to the edge."),
    "pirs": dict(PTCH="Controls the basic pitch of the rim shot.", DEC=DEC, HARD=HARD, RING=RING,
                 RVOL=RVOL, RDEC=RDEC),
    "piml": dict(PTCH="Controls the basic pitch of the sound.", DEC=DEC, HARD=HARD,
                 TENS="Regulates the effect of a hard hit."),
    "pima": dict(DEC="Sets the decay time of the maraca.", GRNS="Adjusts the number of grains in the maraca.",
                 GLEN="Adjusts the decay time for the individual grains.",
                 SIZE="Regulates the size of the maraca.", HARD="Regulates the hardness of the grains."),
    "pihh": dict(PTCH="Controls the basic pitch of the hi hat.", DEC="Sets the decay time of the hi hat.",
                 CLSN="Simulates slight contact between the two cymbals of the hihats.",
                 RING="Controls the amount of ringing in the sound.",
                 AG="Enhances the high frequencies of the sound.",
                 AU="Decreases the high frequencies of the sound.",
                 BR="Controls the low frequences of the sound.",
                 CLOS="Time to closing the hi hat. 127 means it does not close."),
}
