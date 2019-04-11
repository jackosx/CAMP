
# Human Readable / JSON Compatible
genres_readable = [
    {
        "name": "Rock",
        "channel": 0,
        "drums":[{"halves": ['f2', 'f2'],
                  "quarters"   : ['c3', 'c3', 'c3', 'c3'],
                  "eighths"    : ['d2', 'd2','d2', 'd2',
                                  'd2', 'd2','d2', 'd2'],
                  "sixteenths" : ['a#2','a#2','a#2','a#2',
                                   'a#2','a#2','a#2','a#2',
                                   'a#2','a#2','a#2','a#2',
                                   'a#2','a#2','a#2','a#2',]
                       },
                  {"halves": ['f2', 'f2'],
                             "quarters"   : ['f2', 'f2', 'f2', 'f2'],
                             "eighths"    : ['d2', 'd2','d2', 'd2',
                                             'b2', 'd#1','d2', 'd2'],
                             "sixteenths" : ['a#2','a#2','a#2','a#2',
                                              'a#2','a#2','a#2','a#2',
                                              'a#2','a#2','a#2','a#2',
                                              'a#2','a#2','a#2','a#2',]
                                  }],
       "guitar":{},
       "bass":{}

    },
    {
        "name": "Jazz",
        "channel": 1,
        "drums":[{"halves" : [],
                   "quarters" : [],
                   "eighths" : [],
                   "sixteenths" : []},
                 {"halves":[],
                   "quarters":[],
                   "eighths":[],
                   "sixteenths":[]}],
       "guitar":{},
       "bass":{}
    },
    {
        "name": "Country",
        "channel": 2,
        "drums":[{"halves" : [],
                   "quarters" : [],
                   "eighths" : [],
                   "sixteenths" : []},
                 {"halves":[],
                   "quarters":[],
                   "eighths":[],
                   "sixteenths":[]}],
       "guitar":{},
       "bass":{}
    },
]

class Genre(object):
    """Python Genre Class"""
    def __init__(self, genre_dict):
        self.name = genre_dict["name"]
        self.channel = int(genre_dict["channel"])
        self.drums = [GenreDrums(x) for x in genre_dict["drums"]] # TODO
        self.guitar = genre_dict["guitar"]
        self.bass = genre_dict["bass"]
    def __repr__(self):
        return self.name

class GenreDrums(object):
    """GenreDrums."""
    def __init__(self, note_dict):
        self.halves = note_dict["halves"]
        self.quarters  = note_dict["quarters"]
        self.eighths= note_dict["eighths"]
        self.sixteenths = note_dict["sixteenths"]

genre_list = [Genre(g) for g in genres_readable]
