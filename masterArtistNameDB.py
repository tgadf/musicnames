from ioUtils import getFile, saveFile
from fsUtils import isFile
from sys import prefix
from os import getcwd
from os.path import join
from searchUtils import findNearest

class masterArtistNameDB:
    def __init__(self, source, debug=False, init=False):
        self.debug = debug
        if debug:
            print("="*25,"masterArtistNameDB","="*25)
        self.debug  = debug
        self.source = source
        
        self.artistNameDBname      = join(prefix, 'musicnames', "{0}ArtistNameDB.p".format(source))
        self.dbRenamesname         = join(prefix, 'musicnames', "{0}DBRenames.yaml".format(source))
        if self.debug:
            print("  Loading data from {0}".format(self.artistNameDBname))
        if isFile(self.artistNameDBname) and init == False:
            self.artistNameDB = getFile(self.artistNameDBname)
        else:
            if self.debug:
                print("  Initializing a fresh DB for {0}".format(self.source))
            self.artistNameDB = {}
        self.checkForRecursives()
        self.loadRenames()
        if self.debug:
            print("  There are currently {0} artist keys.".format(len(self.artistNameDB)))
            print("  There are currently {0} renamed artist keys.".format(len(self.dbRenames)))

        
    ##########################################################################################
    # Global Getting Function
    ##########################################################################################
    def renamed(self, artistName):
        if self.dbRenames.get(artistName) is not None:
            return self.dbRenames[artistName]
        return artistName
        
        
        
    ##########################################################################################
    # Saving Function
    ##########################################################################################
    def save(self):
        print("Saving {0} artist keys to {1}".format(len(self.artistNameDB), self.artistNameDBname))
        saveFile(idata=self.artistNameDB, ifile=self.artistNameDBname, debug=True)
        
    def loadRenames(self):
        self.dbRenames = {}
        for artistName,namesToBeFixed in self.artistNameDB.items():
            for nameToBeFixed in namesToBeFixed:
                self.dbRenames[nameToBeFixed] = artistName
        
    def saveRenames(self):
        print("Saving {0} renamed artist keys to {1}".format(len(self.dbRenames), self.dbRenamesname))
        saveFile(idata=self.dbRenames, ifile=self.dbRenamesname, debug=True)
        
        
    def forceReloadNames(self, artistNameDB, save=False):
        print("Forcing Reload Using {0} Rename Names".format(len(artistNameDB)))
        dbRenames = {}
        for artistName,namesToBeFixed in artistNameDB.items():
            for nameToBeFixed in namesToBeFixed:
                dbRenames[nameToBeFixed] = artistName
        print("  Forced reload of {0} artist names".format(len(dbRenames)))
        print("  Found {0} renamed names".format(len(artistNameDB)))
        self.checkForRecursives(artistNameDB)
        
        self.artistNameDB = artistNameDB
        self.dbRenames    = dbRenames
        if save is True:
            print("Will save everything")
            self.save()
            self.loadRenames()
            self.saveRenames()
            
            
    def forceReload(self, dbRenames, save=False):
        self.forceReloadRenames(dbRenames, save)
        
    def forceReloadRenames(self, dbRenames, save=False):
        print("Forcing Reload Using {0} Rename Entries".format(len(dbRenames)))
        artistNameDB = {}
        for olderArtistName,fixedArtistName in dbRenames.items():
            if artistNameDB.get(fixedArtistName) is None:
                artistNameDB[fixedArtistName] = []
            artistNameDB[fixedArtistName].append(olderArtistName)
        print("  Forced reload of {0} artist names".format(len(artistNameDB)))
        print("  Found {0} names".format(len(dbRenames)))
        self.checkForRecursives()
        
        self.artistNameDB = artistNameDB
        self.dbRenames    = dbRenames
        if save is True:
            print("Will save everything")
            self.save()
            self.loadRenames()
            self.saveRenames()
            
        

    
    
    ##########################################################################################
    # Finder Functions
    ##########################################################################################
    def findArtist(self, artistName):
        matches = findNearest(artistName, list(self.artistNameDB.keys()), 3, cutoff=0.85)
        for matchName,renameNames in {matchName: self.artistNameDB[matchName] for matchName in matches}.items():
            print(matchName)
            for renameName in renameNames:
                print("\t",renameName)

    
    ##########################################################################################
    # I/O
    ##########################################################################################
    def createRenamesFromDB(self, mdbmap, dbRenames):
        artistNameDB = {x[0]: [] for x in mdbmap.getArtists()}

        for olderArtistName,fixedArtistName in dbRenames.items():
            if artistNameDB.get(olderArtistName) is not None:
                raise ValueError("Can not add recursive definition! Key [{0}] and Value [{1}]".format(artistNameDB.get(olderArtistName),olderArtistName))

        for olderArtistName,fixedArtistName in dbRenames.items():
            if artistNameDB.get(fixedArtistName) is None:
                artistNameDB[fixedArtistName] = []
            artistNameDB[fixedArtistName].append(olderArtistName)
                   
        saveFile(idata=artistNameDB, ifile=self.artistNameDBname)
        
        
    def removeArtist(self, artistName):
        if self.artistNameDB.get(artistName) is not None:
            print("Removing {0} from artist keys".format(artistName))
            del self.artistNameDB[artistName]
            self.save()
            self.loadRenames()
            self.saveRenames()
        else:
            print("Could not not find {0} in artist keys.".format(artistName))
            
            
    def getRenames(self):
        return self.dbRenames
    
    def getArtistNames(self):
        return self.artistNameDB
    
    
    def addRenames(self, dbRenames):
        print("Trying to add {0} renamed artist keys".format(len(dbRenames)))
        for olderArtistName,fixedArtistName in dbRenames.items():
            if self.artistNameDB.get(olderArtistName) is not None:
                raise ValueError("Can not add recursive definition! Key [{0}] and Value [{1}]".format(self.artistNameDB.get(olderArtistName),olderArtistName))
                
        print("There are currently {0} artist keys.".format(len(self.artistNameDB)))
        print("There are currently {0} renamed artist keys.".format(len(self.dbRenames)))
        for olderArtistName,fixedArtistName in dbRenames.items():
            self.dbRenames[olderArtistName] = fixedArtistName
            if self.artistNameDB.get(fixedArtistName) is None:
                self.artistNameDB[fixedArtistName] = []
            self.artistNameDB[fixedArtistName].append(olderArtistName)
        print("There are currently {0} artist keys.".format(len(self.artistNameDB)))
        print("There are currently {0} renamed artist keys.".format(len(self.dbRenames)))
        self.checkForRecursives()
    
        
    def checkForRecursives(self, artistNameDB=None):
        if artistNameDB is None:
            artistNameDB = self.artistNameDB
        for artistName,namesToBeFixed in artistNameDB.items():
            for nameToBeFixed in namesToBeFixed:
                if self.artistNameDB.get(nameToBeFixed) is not None:
                    raise ValueError("Recursive found! Key [{0}] and Values [{1},{2}]".format(artistName,nameToBeFixed,self.artistNameDB.get(nameToBeFixed)))