def getIgnoreArtistList():

    ###########################################################################################################################
    # Ignore List
    ############################################################################################################################
    ignoreArtistList = {}
    ignoreArtistList["Discogs"]  = ["M", "Bernard Edwards & Nile Rodgers", "Pomus-Shuman", "Tepper-Bennett"]
    ignoreArtistList["LastFM"]   = ["MAX", "Sonny Boy Williamson", "Trouble", "NRG", "Olivia", "Hunter", "Zeus", "Cobra", 
                                    "Shogun", "Nomad", "Juice", "Tyrant", "Willow", "Airbag", "Deuce", "Budgie", "Eclipse",
                                    "Jumbo", "L.E.J.", "Sniper", "Ceremony", "Voyager", "Solange", "Logos", 
                                    "The Highwaymen", "Rose", "Blake", "Tash", "Cast", "Friends", "Collage", "Ripe", 
                                    "Undercover", "Quest", "Holden"]

    ignoreArtistList["LastFM"]  += ["Íåèçâåñòíûé Èñïîëíèòåëü", "Coast To Coast AM - George Noory", 
                                    "[unknown]", "Various Composers", "[unknown]", "Zåìôèðà", 'Nature Sounds']
    ignoreArtistList["AllMusic"] = ["Bryan Adams", "Tina"]
    ignoreArtistList["MusicBrainz"] = ["Various Artists", "[unknown]", "[no artist]", "[language instruction]",
                                      "[nature sounds]", "Die drei ???", "[dialogue]", "初音ミク", '[data]', 
                                       'Geovanni', "Juan Torres", "DrefQuila", '[Disney]', 
                                       '[Christmas music]', 'Harry Nach', 'Tiago PZK']
    ignoreArtistList["RateYourMusic"] = []
    ignoreArtistList["Genius"] = []
    ignoreArtistList["KWorbiTunes"] = []
    ignoreArtistList["KWorbSpotify"] = []
    ignoreArtistList["Deezer"] = []
    ignoreArtistList["AlbumOfTheYear"] = []
    ignoreArtistList = {db: {k: True for k in x} for db, x in ignoreArtistList.items()}
    
    return ignoreArtistList