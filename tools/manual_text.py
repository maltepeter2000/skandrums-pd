"""Texts from the Elektron Machinedrum manual (OS 1.63), Appendix A,
taken from the original PDF. Every control of all 30 voices has an entry."""

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

# ---- added from the original PDF (Appendix A, OS 1.63) ----
MOD = "The frequency modulation depth."
MFRQ = "The modulation frequency."
MDEC = "The modulation decay time."
FB = "Feedback amount."
HPF_F = "High pass filter frequency."
RAMP_D = "The pitch ramp depth."
RDEC_D = "The pitch ramp decay time. A higher value gives a longer decay."
GRAB = ("Sets the time to grabbing the cymbal. A value of 127 means "
        "that the cymbal is never grabbed.")

PARAMS.update({
    "trxsd": dict(PTCH=PTCH, DEC=DEC, BUMP="Adds a pitch shift at the start.",
                  BENV="Controls the envelope of the bump.", SNAP="Amount of snap.",
                  TONE="Changes tonal quality.", TUNE="Detunes the drum.",
                  CLIP="A special type of distortion."),
    "efmbd": dict(PTCH=PTCH, DEC=DEC, RAMP=RAMP_D, RDEC=RDEC_D, MOD=MOD, MFRQ=MFRQ,
                  MDEC=MDEC, MFB="Modulation feedback."),
    "efmsd": dict(PTCH=PTCH, DEC=DEC, NOIS="The amount of noise in the snare drum.",
                  NDEC="Noise decay time.", MOD=MOD, MFRQ=MFRQ, MDEC=MDEC, HPF=HPF_F),
    "efmxt": dict(PTCH=PTCH, DEC=DEC, RAMP=RAMP_D, RDEC=RDEC_D, MOD=MOD, MFRQ=MFRQ,
                  MDEC=MDEC, CLIC="Adds a click to the start of the drum."),
    "efmcp": dict(PTCH=PTCH, DEC=DEC, CLPS="The number of claps.",
                  CDEC="The clap decay time. A higher value gives a longer decay.",
                  MOD=MOD, MFRQ=MFRQ, MDEC=MDEC, HPF=HPF_F),
    "efmrs": dict(PTCH=PTCH, DEC=DEC, MOD=MOD, HPF=HPF_F,
                  SNAR="Adds snare drum timbre to the sound.",
                  SPTC="The pitch of the snare drum timbre.",
                  SDEC="The decay of the snare drum timbre.",
                  SMOD="The modulation depth of the snare drum timbre."),
    "efmcb": dict(PTCH="Controls the basic pitch.", DEC=DEC,
                  SNAP="The amount of snap in the beginning of the sound.", FB=FB,
                  MOD=MOD, MFRQ=MFRQ, MDEC=MDEC),
    "efmhh": dict(PTCH="Controls the basic pitch of the hihat.", DEC=DEC,
                  TREM="Depth of the added tremolo.", TFRQ="Frequency of the tremolo.",
                  MOD=MOD, MFRQ=MFRQ, MDEC=MDEC, FB=FB),
    "efmcy": dict(PTCH="Controls the basic pitch of the cymbal.", DEC=DEC, FB=FB,
                  HPF=HPF_F, MOD=MOD, MFRQ=MFRQ, MDEC=MDEC),
    "pirc": dict(PTCH="Controls the basic pitch of the ride.", DEC="Sets the decay time of the ride.",
                 HARD="Adds the impression of a hard hit.",
                 RING="Controls the amount of ringing in the sound.",
                 AG="Enhances the high frequencies of the sound.",
                 AU="Decreases the high frequencies of the sound.",
                 BR="Controls the low frequences of the sound.", GRAB=GRAB),
    "picc": dict(PTCH="Controls the basic pitch of the crash.", DEC="Sets the decay time of the crash.",
                 HARD="Adds the impression of a hard hit.",
                 RING="Controls the amount of ringing in the sound.",
                 AG="Enhances the high frequencies of the sound.",
                 AU="Decreases the high frequencies of the sound.",
                 BR="Controls the low frequences of the sound.", GRAB=GRAB),
})
# the OH page lists the same parameters as CH
PARAMS["trxoh"] = dict(PARAMS["trxch"])
FAMILY["efm"] = ("Enhanced Feedback Modulation",
                 'Manual: "The EFM MD-synth introduces Elektron\'s Enhanced Feedback Modulation algorithms."')
