from sys import prefix
from uuid import uuid4
from fsUtils import isDir, isFile, setFile, setDir, mkDir
from fileIO import fileIO
from listUtils import getFlatList
from timeUtils import timestat
from masterDBGate import masterDBGate
from pandas import Series, DataFrame


class mergerExpo:
    def __init__(self, debug=False):
        self.expo = {"Discogs": 10, "AllMusic": 10, "MusicBrainz": 42, "LastFM": 14, "RateYourMusic": 10, 
                    "Deezer": 12, "AlbumOfTheYear": 9, "Genius": 11, "KWorbSpotify": 15, "KWorbiTunes": 15}
        
        self.io = fileIO()
    
    def getExpo(self):
        return self.expo
        
    def findMergerPrefixExpo(self):
        ts = timestat("Finding Merger Prefix")        
        
        self.mDBGate = masterDBGate()
        self.dbDiscs = self.mDBGate.getDiscs()
        
        basename = "IDToName"
        maxIDs   = {}
        saveVal  = {}
        for db,dbDisc in self.dbDiscs.items():
            savename = setFile(dbDisc.getDiscogDBDir(), "Artist{0}PreMerge.p".format(basename))
            maxIDs[db] = max([int(x) for x in self.io.get(savename).index if x is not None])

        for db,maxID in maxIDs.items():
            exp = int(ceil(log10(maxID)))
            print("{0: <15}{1: >45}{2: >4}".format(db,maxID,exp))
            preMaxID = int(pow(10,exp+3))+maxID
            print("{0: <15}{1: >45}{2: >4}".format("",preMaxID,exp))
            saveVal[db] = exp+3
            
        ts.stop()
        
        from json import dumps
        print(dumps(saveVal))
        
        return saveVal
    

class masterArtistMerger:
    def __init__(self, install=False, debug=False):
        self.debug   = debug
        self.mergers = {}
        print("{0} masterArtistMerger {1}".format("="*25,"="*25))

        self.io = fileIO()

        self.musicNamesDir = setDir(prefix, 'musicnames')
        self.initializeData() if install is False else self.installData()

    
    def initializeData(self):
        mExpo = mergerExpo()
        self.prefixExpo = mExpo.getExpo()
        
        self.manualMergers = self.getData(fast=True, local=False)
        self.setMergerMapping()
        self.summary()
        
        
    def installData(self):
        if not isDir(self.musicNamesDir):
            print("Install: Making Prefix Dir [{0}]".format(self.musicNamesDir))
            mkDir(self.musicNamesDir)
        if not isFile(self.getFilename(fast=True, local=False)):
            print("Install: Creating Prefix Data From Local Data")
            self.writeToMainPickleFromLocalYAML()
        
            
    def summary(self, manualMergers=None):
        manualMergers = self.manualMergers if manualMergers is None else manualMergers
        print("masterArtistMerger Summary:")
        print("  DB ID Entries: {0}".format(len(self.dbIDTomIDMapping)))
        print("  DB Entries:    {0}".format(len(self.mIDMapping)))
        print("  Artists:       {0}".format(len(self.manualMergers)))

            
    #########################################################################################################
    #
    # Lookup Maps
    #
    #########################################################################################################    
    def setMergerMapping(self):
        ## For Getting All Mergers By DB
        mDBGate = masterDBGate()
        dbMappingDF = self.manualMergers.apply(Series)
        dbMapping   = {db: dbMappingDF[db] for db in mDBGate.getDBs()}
        dbMapping   = {db: dbData[dbData.notna()] for db,dbData in dbMapping.items()}
        self.dbMapping = dbMapping
        

        ## For Getting All Mergers By Merger ID
        mIDMapping = {}
        for artistName,artistData in self.manualMergers.iteritems():
            for db,dbData in artistData.items():
                mID   = dbData["ID"]
                mData = dbData["MergeData"]
                if mIDMapping.get(mID) is not None:
                    raise ValueError("There are multiple merge IDs [{0}]".format(mID))
                mIDMapping[mID] = {"ArtistName": artistName, "DB": db, "MergeData": mData}
        self.mIDMapping = mIDMapping
        
        
        ## For Getting Merger ID By DB+DBID
        dbIDTomIDMapping = {}
        for artistName,artistData in self.manualMergers.iteritems():
            for db,dbData in artistData.items():
                mID   = dbData["ID"]
                mData = dbData["MergeData"]
                for dbID,dbIDData in mData.items():
                    key = tuple([db,dbID])
                    if dbIDTomIDMapping.get(key) is not None:
                        print("DB ({0} ID [{1}] is matched for multiple merger IDs ({2})".format(db,dbID,artistName))
                        print({"ArtistName": artistName, "DB": db, "MergeID": mID})
                        print(dbIDTomIDMapping[key])
                    dbIDTomIDMapping[key] = {"ArtistName": artistName, "MergeID": mID}
        self.dbIDTomIDMapping = dbIDTomIDMapping

            
    #########################################################################################################
    #
    # Merger ID Generation
    #
    #########################################################################################################    
    def genMergerID(self, db):
        uint = uuid4().int
        expo = self.prefixExpo.get(db)
        if expo is None:
            raise ValueError("DB [{0}] does not have an exponent in the master artist merger data")
        mID = int(str(uint)[-(expo-3):]) + int(pow(10,expo))
        mID = str(mID)
        if self.debug:
            print(db,' \t',expo,'\t',len(str(uint)),'\t',uint,'\t',mID)
        return mID

            
    #########################################################################################################
    #
    # I/O
    #
    #########################################################################################################
    def getFilename(self, fast, local):
        basename="manualMergers"
            
        self.localpfname = "{0}.p".format(basename)
        self.localyfname = "{0}.yaml".format(basename)
        self.pfname = setFile(self.musicNamesDir, self.localpfname)
        self.yfname = setFile(self.musicNamesDir, self.localyfname)
        
        if fast is True:
            if local is True:
                return self.localpfname
            else:
                return self.pfname
        else:
            if local is True:
                return self.localyfname
            else:
                return self.yfname
            
        raise ValueError("Somehow didn't get a filename!")

    def getData(self, fast=True, local=False):
        ftype = {True: "Pickle", False: "YAML"}
        ltype = {True: "Local", False: "Main"}
        ts = timestat("Getting Manual Mergers Data From {0} {1} File".format(ltype[local], ftype[fast]))
        fname = self.getFilename(fast, local)
        manualMergers = self.io.get(fname)

        ts.stop()
    
        return manualMergers

    def writeToLocalYamlFromMainPickle(self):
        ts = timestat("Writing To Local YAML From Main Pickle")
        manualMergers = self.getData(fast=True, local=False)
        self.saveData(manualMergers, fast=False, local=True)
        ts.stop()

    def writeToMainPickleFromLocalYAML(self):
        ts = timestat("Writing To Main Pickle From Local YAML")
        manualMergers = self.getData(fast=False, local=True)
        self.saveData(manualMergers, fast=True, local=False)
        ts.stop()
        
    def saveData(self, manualMergers=None, fast=True, local=False):
        ftype = {True: "Pickle", False: "YAML"}
        ltype = {True: "Local", False: "Main"}
        ts = timestat("Saving Manual Mergers Data To {0} {1} File".format(ltype[local], ftype[fast]))
        manualMergers = self.manualMergers if manualMergers is None else manualMergers
        #self.summary(manualMergers)
        
        fname = self.getFilename(fast, local)
        if fast:
            toSave = Series(manualMergers) if isinstance(manualMergers, dict) else manualMergers
            toSave = toSave.sort_index()
        else:
            toSave = manualMergers.sort_index().to_dict() if isinstance(manualMergers, Series) else manualMergers
        self.io.save(idata=toSave, ifile=fname)
        
        ts.stop()

            
    #########################################################################################################
    #
    # Getter Functions
    #
    #########################################################################################################
    def getArtistDataByName(self, artistName):
        return self.manualMergers[artistName] if self.manualMergers.__contains__(artistName) else None
    
    def getArtistDBDataByName(self, artistName, db):
        artistData = self.getArtistDataByName(artistName)
        return artistData.get(db) if isinstance(artistData,dict) else None
    
    def getMergerDataByDB(self, db):
        return self.dbMapping[db] if self.dbMapping.get(db) is not None else None
    
    def getMergedIDsByDB(self, db):
        return getFlatList([x["MergeData"].keys() for x in self.getMergerDataByDB(db).values])
    
    def getMergedIDs(self):
        return getFlatList([self.getMergedIDsByDB(db) for db in self.dbMapping.keys()])
    
    def getArtistDataByMergerID(self, mID):
        return self.mIDMapping[mID] if self.mIDMapping.get(mID) is not None else None
    
    def getMergerIDByDBID(self, db, dbID):
        key = tuple([db,dbID])
        return self.dbIDTomIDMapping[key] if self.dbIDTomIDMapping.get(key) is not None else None

            
    #########################################################################################################
    #
    # Merge/Update Data
    #
    #########################################################################################################
    def mergeDict(self, dict1, dict2):
        return {**dict1, **dict2}

    def merge(self, newData, save=True, debug=True):
        for artistName,artistData in newData.items():
            print("Merging {0}".format(artistName))
            artistMergeData = self.getArtistDataByName(artistName)
            if artistMergeData is None:
                if debug:
                    print("  Adding New Artist [{0}] To Data".format(artistName))
                    for db,dbData in artistData.items():
                        print("    Adding New DB [{0}] With [{1}] IDs To Artist Data [{2}]".format(db,len(dbData),artistName))
                newMergeData = {db: {"ID": self.genMergerID(db), "MergeData": dbData} for db,dbData in artistData.items()}
            else:
                newMergeData = artistMergeData
                for db,dbData in artistData.items():
                    if newMergeData.get(db) is None:
                        if debug:
                            print("  Adding New DB [{0}] With [{1}] IDs To Artist Data [{2}]".format(db,len(dbData),artistName))
                        newMergeData[db] = {"ID": self.genMergerID(db), "MergeData": dbData}
                    else:
                        if debug:
                            print("  Adding New DB IDs [{0}] To Existing [{1}] IDs To Artist DB Data [{2}/{3}]".format(len(dbData),len(artistMergeData[db]["MergeData"]),artistName,db))
                        newMergeData[db] = {"ID": artistMergeData[db]["ID"], "MergeData": self.mergeDict(dbData, newMergeData[db]["MergeData"])}
                        
            self.manualMergers[artistName] = newMergeData
            
        if save:
            self.saveData(local=False, fast=True)
            self.setMergerMapping()
            self.summary()