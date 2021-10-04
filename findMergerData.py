from masterArtistMerger import masterArtistMerger
from masterDBGate import musicDBs
from timeUtils import timestat
from ioUtils import getFile, saveFile
from pandas import DataFrame

class findMergerData:
    def __init__(self, dbNameRefData=None):
        self.mam = masterArtistMerger()        
        
        self.mDBs = musicDBs()
        self.dbDiscs = self.mDBs.getDiscs()
        
        if dbNameRefData is None:
            ts = timestat("Getting DB Artist PreMerge Names and Refs")
            dbNames = {db: dbDisc.getArtistIDToPreMergeNameData() for db,dbDisc in self.dbDiscs.items()}
            ts.update()
            dbRefs  = {db: dbDisc.getArtistIDToPreMergeRefData() for db,dbDisc in self.dbDiscs.items()}
            ts.update()
            self.dbNameRefData = {db: DataFrame(dbNames[db], columns=["Name"]).join(DataFrame(dbRefs[db], columns=["Ref"])) for db in dbNames.keys()}
            ts.stop()
        else:
            self.dbNameRefData = dbNameRefData
        
        self.savename = "newMergeData.yaml"

        
    def getDBNameRefData(self):
        return self.dbNameRefData
        

    def findArtistData(self, artistName):
        result = {db: dbData[dbData["Name"].apply(lambda x: artistName in x if x is not None else False)] for db,dbData in self.dbNameRefData.items()}
        result = {db: dbResult.T.to_dict() for db,dbResult in result.items() if dbResult.shape[0] > 0}
        retval = {}
        for db,dbResult in result.items():
            mamResult = self.mam.getArtistDBDataByName(artistName, db)
            mamResult = mamResult.get("MergeData") if isinstance(mamResult,dict) else None
            if mamResult is not None:
                newResult = {dbID: dbIDData for dbID,dbIDData in result[db].items() if dbID not in mamResult.keys()}
                if len(newResult) > 1:
                    retval[db] = newResult
            else:
                if len(result[db]) > 1:
                    retval[db] = result[db]
        
        if len(retval) > 0:
            print("Saving [{0}] DBs For Artist [{1}] To [{2}]".format(len(retval), artistName, self.savename))
            saveFile(idata={artistName: retval}, ifile=self.savename)
        else:
            print("Didn't find any DB results for [{0}]".format(artistName))
            
