from ioUtils import getFile, saveFile
from fsUtils import isDir, setDir, setFile, isFile, mkDir
from timeUtils import timestat
from pandas import Series
from sys import prefix

class masterArtistNameDB:
    def __init__(self, source, install=False, debug=False):
        self.debug = debug
        print("{0} masterArtistNameDB(\"{1}\") {2}".format("="*25,source,"="*25))
        self.debug  = debug
        self.source = source
        
        self.musicNamesDir = setDir(prefix, 'musicnames')
        self.initializeData() if install is False else self.installData()
    
    def initializeData(self):
        self.manualRenames = self.getData(fast=True, local=False)
        retval,manualRenames  = self.duplicateIndexTest()
        if retval is False:
            raise ValueError("There are duplicate key,values in the [{0}] data".format(self.source))
        self.manualRenames = manualRenames
        retval = self.recursiveTest()
        if retval is False:
            raise ValueError("There are recursive key,values in the [{0}] data".format(self.source))
        self.summary()
        
    def installData(self):
        if not isDir(self.musicNamesDir):
            print("Install: Making Prefix Dir [{0}]".format(self.musicNamesDir))
            mkDir(self.musicNamesDir)
        if not isFile(self.getFilename(fast=True, local=False)):
            print("Install: Creating Prefix Data From Local Data")
            self.writeToMainPickleFromLocalYAML()
                        
    def summary(self, manualRenames=None):
        manualRenames = self.manualRenames if manualRenames is None else manualRenames
        print("masterArtistNameDB(\"{0}\") Summary:".format(self.source))
        print("  Entries: {0}".format(len(manualRenames)))
        print("  Artists: {0}".format(manualRenames.nunique()))

            
    #########################################################################################################
    #
    # I/O
    #
    #########################################################################################################
    def getFilename(self, fast, local):
        basename="ManualRenames"
            
        self.localpfname = "{0}{1}.p".format(self.source, basename)
        self.localyfname = "{0}{1}.yaml".format(self.source, basename)
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
        ts = timestat("Getting Manual Renames Data From {0} {1} File".format(ltype[local], ftype[fast]))
        fname = self.getFilename(fast, local)
        manualRenames = getFile(fname)

        ts.stop()
    
        return manualRenames

    def writeToLocalYamlFromMainPickle(self):
        ts = timestat("Writing To Local YAML From Main Pickle")
        manualRenames = self.getData(fast=True, local=False)
        self.saveData(manualRenames, fast=False, local=True)
        ts.stop()

    def writeToMainPickleFromLocalYAML(self):
        ts = timestat("Writing To Main Pickle From Local YAML")
        manualRenames = self.getData(fast=False, local=True)
        self.saveData(manualRenames, fast=True, local=False)
        ts.stop()
        
    def saveData(self, manualRenames=None, fast=True, local=False):
        ftype = {True: "Pickle", False: "YAML"}
        ltype = {True: "Local", False: "Main"}
        ts = timestat("Saving Manual Renames Data To {0} {1} File".format(ltype[local], ftype[fast]))
        manualRenames = self.manualRenames if manualRenames is None else manualRenames
        #self.summary(manualRenames)
        
        fname = self.getFilename(fast, local)
        if fast:
            toSave = Series(manualRenames) if isinstance(manualRenames, dict) else manualRenames
            toSave = toSave.sort_values()
        else:
            toSave = manualRenames.to_dict() if isinstance(manualRenames, Series) else manualRenames
        saveFile(idata=toSave, ifile=fname)
        
        ts.stop()
        
        
    ##########################################################################################
    #
    # Assert/Consistency
    #
    ##########################################################################################
    def duplicateIndexTest(self, manualRenames=None):
        manualRenames = self.manualRenames if manualRenames is None else manualRenames
        manualRenames = Series(manualRenames) if not isinstance(manualRenames, Series) else manualRenames
        
        err = False
        for index in manualRenames.index[manualRenames.index.duplicated()]:
            if manualRenames[index].nunique() > 1:
                print("Found Multiple Values For Same Index [{0}]".format(index))
                for key,value in manualRenames[index].iteritems():            
                    print("{0: >50} <-> {1: <50}".format(key,value))
                    err = True

        _ = print("  No duplicate key/values in manual renames") if err is False else None
        manualRenames = Series(manualRenames.to_dict()) if err is False else manualRenames
        retval = not err
        return retval,manualRenames
        
    def recursiveTest(self, manualRenames=None):
        manualRenames = self.manualRenames if manualRenames is None else manualRenames
        manualRenames = Series(manualRenames) if not isinstance(manualRenames, Series) else manualRenames
        
        retval = manualRenames[manualRenames.apply(lambda x: manualRenames.index.__contains__(x))]
        if retval.shape[0] == 0:
            print("  No recursive key/values in manual renames")
            return True
        else:
            recursives = retval.unique()
            print("="*105)
            print("Found {0} recursive key/values in manual renames".format(len(recursives)))
            for artistName in recursives:
                print("{0: >50} <-> {1: <50}".format(artistName,manualRenames[artistName]))
            print("="*105)
        return False

        
    ##########################################################################################
    #
    # Global Getting Function
    #
    ##########################################################################################
    def renamed(self, artistName):
        if self.manualRenames.index.__contains__(artistName):
            return self.manualRenames[artistName]
        return artistName

        
    ##########################################################################################
    #
    # Merge
    #
    ##########################################################################################
    def merge(self, newRenames, test=False):
        print("Merging New Renames With Master Renames Data")
        newRenames = Series(newRenames) if not isinstance(newRenames, Series) else newRenames
        testManualRenames = self.manualRenames.append(newRenames)
        
        retval,testManualRenames  = self.duplicateIndexTest(testManualRenames)
        if retval is False:
            raise ValueError("There are duplicate key,values in the merged data".format())
        retval = self.recursiveTest(testManualRenames)
        if retval is False:
            raise ValueError("There are recursive key,values in the merged data".format())
            
        if test is False:
            self.saveData(fast=True, local=False)
            self.saveData(fast=False, local=True)
        else:
            print("Only Testing The Machinery And Not Saving Results")