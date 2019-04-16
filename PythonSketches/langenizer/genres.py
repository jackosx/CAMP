import json

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

with open('genres.json') as json_file:  
    genres = json.load(json_file) 
    genre_list = [Genre(g) for g in genres]
