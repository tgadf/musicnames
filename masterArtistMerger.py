from sys import prefix
from os import getcwd
from os.path import join
from searchUtils import findNearest
from fsUtils import isDir, isFile, setFile
from ioUtils import getFile, saveFile
from timeUtils import timestat

class masterArtistMerger:
    def __init__(self, debug=False):
        self.debug   = debug
        self.mergers = {}
        
        self.DBIDtoArtistName = {}
        self.DBIDtoNewID      = {}
                
        self.mergerDir = join(prefix, 'musicnames', 'mergers')
        if not isDir(self.mergerDir):
            raise ValueError("There is no master merger directory [{0}]".format(self.mergerDir))
            
        self.dbs = ["MusicBrainz", "AllMusic", "Discogs", "Deezer", "Genius", "AlbumOfTheYear", "LastFM",
                    "RateYourMusic", "KWorbSpotify", "KWorbiTunes"]
        ts = timestat("Loading Merged Artist Data")
        self.setArtistMergers()
        ts.stop()
            
      
    ########################################################################################################################
    #
    #
    # Multi-Artist Information
    #
    #
    ########################################################################################################################
    def getNewID(self, db, IDstoMerge):
        if len(IDstoMerge) == 0:
            raise ValueError("IDs to Merge is 0 for DB [{0}]".format(db))
        
        if db == "MusicBrainz":
            newID  =  int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += int(1e41)
            newID  = str(int(newID))
        elif db == "Discogs":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e11
            newID  = str(int(newID))
        elif db == "AllMusic":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e11
            newID  = str(int(newID))
        elif db == "Deezer":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e11
            newID  = str(int(newID))
        elif db == "LastFM":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e14
            newID  = str(int(newID))
        elif db == "Genius":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e11
            newID  = str(int(newID))
        elif db == "AlbumOfTheYear":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e11
            newID  = str(int(newID))
        elif db == "RateYourMusic":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e11
            newID  = str(int(newID))
        elif db == "KWorbSpotify":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e14
            newID  = str(int(newID))
        elif db == "KWorbiTunes":
            newID  = int(sum([int(artistID) for artistID in IDstoMerge])/len(IDstoMerge))
            newID += 1e14
            newID  = str(int(newID))
        else:
            raise ValueError("NewID not defined for db {0}".format(db))
            
        return newID
    
    
    def getMergers(self):
        return self.mergers

    
    def getMergersByDB(self, db):
        if self.mergers.get(db) is None:
            return []
        return self.mergers[db]

    
    def getMergersIDToNameByDB(self, db):
        if self.DBIDtoArtistName.get(db) is None:
            return {}
        return self.DBIDtoArtistName[db]
    

    def getAllNewIDs(self):
        newIDs = getFlatList([list(x.keys()) for db,x in self.DBIDtoArtistName.items()])
        return newIDs
        
    def getAllMergedIDs(self):
        allIDs = getFlatList([getFlatList(list(x)) for db,x in self.DBIDtoNewID.items()])
        return allIDs

    

    def setArtistMergers(self):
        for db in self.dbs:
            self.DBIDtoArtistName[db] = {}
            self.DBIDtoNewID[db]      = {}
            IDsToMerge                = []
            
            dbMergerData = self.getDBMergerData(db)
            for artistName, values in dbMergerData.items():
                IDs = list(values.keys())
                IDsToMerge.append(IDs)

                newID = self.getNewID(db, IDs)
                self.DBIDtoNewID[db][tuple(sorted(IDs))] = newID
                self.DBIDtoArtistName[db][newID] = artistName

            self.mergers[db] = IDsToMerge   
            
            
            
    ########################################################################################################################
    #
    #
    # IO and Updates Information
    #
    #
    ########################################################################################################################
    def getDBMergerData(self, db):
        mergerFile = self.getDBMergerFilename(db)
        if not isFile(mergerFile):
            raise ValueError("Could not find mergerFile [{0}]".format(mergerFile))
        dbMergerData = getFile(mergerFile)
        return dbMergerData
    
        
    def getDBMergerFilename(self, db, local=False):
        if local is True:
            mergerFile   = setFile("mergers", "merge{0}.yaml".format(db))
        else:
            mergerFile   = setFile(self.mergerDir, "merge{0}.yaml".format(db))
        return mergerFile
    
    
    def saveDBMergerData(self, db, mergerData, local=False):
        filename = self.getDBMergerFilename(db, local=local)
        ts = timestat("Saving {0} merged artists for {1} DB to {2}".format(len(mergerData), db, filename))
        saveFile(idata=mergerData, ifile=filename)
        ts.stop()
    
    
    def updateMergedData(db, updateData):
        mergeData = self.getDBMergerData(db)
        nOverlap  = set(mergeData.keys()).intersection(set(updateData.keys()))

        if len(nOverlap) == 0:
            print("No Overlap!!")
            print("Before: {0}".format(len(mergeData)))
            print("Update: {0}".format(len(updateData)))
        else:
            print("Found {0} Overlapping Artists".format(nOverlap))

        if len(nOverlap) == 0:
            print("Before: {0}".format(len(mergeData)))
            mergeData.update(updateData)
            print("After:  {0}".format(len(mergeData)))
            self.saveDBMergerData(db=db, mergerData=mergeData, local=True)
            #saveFile(idata=mergeData, ifile="mergers/merge{0}.yaml".format(db), debug=True)