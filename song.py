# -------------------------------------------------------------
# 
# -------------------------------------------------------------

from music import *

# ----------------- CONFIGURATION -----------------
TITLE        = "House - "
TEMPO_BPM    = 124
OUTPUT_MIDI  = "house.mid"

BARS_DEFAULT = 4
STRUCTURE = [
    ("intro", 8), ("verse", 8), ("pre", 4), ("chorus", 8),
    ("verse", 8), ("pre", 4), ("chorus", 8),
    ("bridge", 4), ("chorus", 8), ("outro", 8)
]

TRACKS = {
    "PIANO": (ELECTRIC_PIANO, 0),   
    "BASS":  (FINGERED_BASS, 1),
    "DRUMS": (0, 9),                
}

# ----------------- UTIL PITCH -----------------
_NOTE_TO_SEMITONE = {
    "C":0, "C#":1, "Db":1, "D":2, "D#":3, "Eb":3, "E":4,
    "F":5, "F#":6, "Gb":6, "G":7, "G#":8, "Ab":8, "A":9,
    "A#":10, "Bb":10, "B":11
}
def to_midi(p):
    if isinstance(p, (int, long)): return int(p)
    note, octv = p[:-1].strip(), int(p[-1])
    return (octv + 1) * 12 + _NOTE_TO_SEMITONE[note]

def add_notes(phrase, notes):
    # notes = [(pitch, dur), ...] | pitch = int MIDI o "C4" | REST
    for p, d in notes:
        phrase.addNote(Note(p if p==REST else to_midi(p), d))

def add_chord_stab(phrase, chord_pitches, dur):
    for p in chord_pitches:
        phrase.addNote(Note(to_midi(p), dur))

# ----------------- ARM / PROG -----------------

PROG = [
    (["F3","Ab3","C4"], "F2"),
    (["Db3","F3","Ab3"], "Db2"),
    (["Ab2","C3","Eb3"], "Ab1"),
    (["Eb3","G3","Bb3"], "Eb2"),
]

# ----------------- DRUMS -----------------

def make_drum_layer(pitch, hit_positions, bars, slots_per_bar=16):
    ph = Phrase(0.0)
    for _ in range(bars):
        for s in range(slots_per_bar):
            ph.addNote(Note(pitch if s in hit_positions else REST, SN))
    return ph

def house_kick(bars):
    hits = {0,4,8,12}
    return make_drum_layer(36, hits, bars)

def house_clap(bars):
    hits = {4,12}
    return make_drum_layer(39, hits, bars)

def hat_offbeat(bars):
    hits = {2,6,10,14}
    return make_drum_layer(46, hits, bars)

def hat_closed_16(bars):
    hits = {1,3,5,7,9,11,13,15}
    return make_drum_layer(42, hits, bars)

def shaker_16(bars):
    hits = set(range(16))
    return make_drum_layer(70, hits, bars)

def tom_fill_1bar():
    ph = Phrase(0.0)
    seq = [(45, SN), (47, SN), (48, EN), (REST, SN), (45, SN), (47, SN), (48, EN), (49, EN)]
    for p,d in seq: ph.addNote(Note(p if p==REST else p, d))
    return ph

# ----------------- PATTERNS -----------------
def piano_stabs(bars, density=1.0):
    
    ph = Phrase(0.0)
    prog_len = len(PROG)
    for i in range(bars):
        chords, _ = PROG[i % prog_len]
        
        
        for beat in range(4):
            
            if density >= 1.0 or (density < 1.0 and beat % 2 == 0):
                add_chord_stab(ph, [p.replace("3","4") for p in chords], SN)  
            else:
                add_notes(ph, [(REST, SN)])
            
            add_notes(ph, [(REST, EN - SN)])
    return ph

def bass_groove(bars, swing=False):
   
    ph = Phrase(0.0)
    prog_len = len(PROG)
    for i in range(bars):
        _, root = PROG[i % prog_len]
        low = root
        high = root[0]+str(int(root[1])+1) if len(root)==2 else "F3"  

        add_notes(ph, [(low, EN)])           
        add_notes(ph, [(REST, SN)])          
        add_notes(ph, [(high, SN)])          
        
        add_notes(ph, [(REST, QN)])
        
        add_notes(ph, [(low, EN)])
        add_notes(ph, [(REST, SN)])
        add_notes(ph, [(high, SN)])         
        
        add_notes(ph, [(REST, QN)])
    return ph

def bass_groove_busier(bars):
    
    ph = Phrase(0.0)
    prog_len = len(PROG)
    for i in range(bars):
        _, root = PROG[i % prog_len]
        low = root
        high = root[0]+str(int(root[1])+1) if len(root)==2 else "F3"
        
        add_notes(ph, [(low, EN), (high, EN)])     
        add_notes(ph, [(low, SN), (REST, SN), (REST, EN)])  
        add_notes(ph, [(low, EN), (high, EN)])    
        add_notes(ph, [(high, SN), (REST, EN + SN)])       
    return ph

# ----------------- SECCIONES -----------------
def sec_intro(bars=BARS_DEFAULT):
    piano = piano_stabs(bars, density=0.5)
    bass  = Phrase(0.0)
    hh    = hat_closed_16(bars)
    ohh   = hat_offbeat(bars)
    kick  = house_kick(bars//2)  
    
    if bars >= 2:
        pre_kick = make_drum_layer(REST, set(), bars//2)
        drums_layers = [hh, ohh, pre_kick, kick]
    else:
        drums_layers = [hh, ohh, kick]
    return {"PIANO":[piano], "BASS":[bass], "DRUMS":drums_layers}, bars

def sec_verse(bars=BARS_DEFAULT):
    piano = piano_stabs(bars, density=0.75)
    bass  = bass_groove(bars)
    kick  = house_kick(bars)
    clap  = house_clap(bars)
    ohh   = hat_offbeat(bars)
    shkr  = shaker_16(bars)
    return {"PIANO":[piano], "BASS":[bass], "DRUMS":[kick, clap, ohh, shkr]}, bars

def sec_pre(bars=BARS_DEFAULT):
    
    piano = piano_stabs(bars, density=1.0)
    bass  = bass_groove(bars)
    clap  = house_clap(bars)
    ohh   = hat_offbeat(bars)
    hh    = hat_closed_16(bars)
    
    fill  = tom_fill_1bar(); fill.setStartTime((bars-1) * WN)
    return {"PIANO":[piano], "BASS":[bass], "DRUMS":[clap, ohh, hh, fill]}, bars

def sec_chorus(bars=BARS_DEFAULT):
    piano = piano_stabs(bars, density=1.0)
    bass  = bass_groove_busier(bars)
    kick  = house_kick(bars)
    clap  = house_clap(bars)
    ohh   = hat_offbeat(bars)
    shkr  = shaker_16(bars)
    hh    = hat_closed_16(bars)
    return {"PIANO":[piano], "BASS":[bass], "DRUMS":[kick, clap, ohh, shkr, hh]}, bars

def sec_bridge(bars=BARS_DEFAULT):
    
    piano = piano_stabs(bars, density=0.5)
    bass  = Phrase(0.0)
    clap  = house_clap(bars)
    hh    = hat_closed_16(bars)
    
    roll = Phrase(0.0)
    for _ in range(14): roll.addNote(Note(40, SN))
    roll.addNote(Note(40, EN)); roll.addNote(Note(49, EN))
    roll.setStartTime((bars-1) * WN + QN) 
    return {"PIANO":[piano], "BASS":[bass], "DRUMS":[clap, hh, roll]}, bars

def sec_outro(bars=BARS_DEFAULT):
    
    piano = piano_stabs(bars, density=0.5)
    bass  = bass_groove(bars)
    kick  = house_kick(bars)
    ohh   = hat_offbeat(bars)
    return {"PIANO":[piano], "BASS":[bass], "DRUMS":[kick, ohh]}, bars

SECTIONS = {
    "intro":sec_intro, "verse":sec_verse, "pre":sec_pre,
    "chorus":sec_chorus, "bridge":sec_bridge, "outro":sec_outro
}

# ----------------- MOTOR -----------------
def make_parts(tracks): return {n: Part(n, prog, ch) for n,(prog, ch) in tracks.items()}

def parse_token(tok): return (tok[0], int(tok[1])) if isinstance(tok, tuple) else (tok, BARS_DEFAULT)

def build_score(structure, sections, tracks, title, tempo):
    score = Score(title); score.setTempo(tempo)
    parts = make_parts(tracks); t = 0.0
    for tok in structure:
        name, bars = parse_token(tok); name = name.strip().lower()
        section_dict, bars = sections[name](bars)
        fixed_dur = bars * WN
        for track, value in section_dict.items():
            phs = value if isinstance(value, list) else [value]
            for ph in phs:
                ph.setStartTime(t)
                parts[track].addPhrase(ph)
        t += fixed_dur
    for p in parts.values(): score.addPart(p)
    return score

# ----------------- RUN -----------------
if __name__ == "__main__":
    sc = build_score(STRUCTURE, SECTIONS, TRACKS, TITLE, TEMPO_BPM)
    Play.midi(sc)
    Write.midi(sc, OUTPUT_MIDI)
    print("✅ MIDI exportado:", OUTPUT_MIDI)
