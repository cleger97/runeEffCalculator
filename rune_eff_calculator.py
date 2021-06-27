import csv
import os
import sys
import json
import math
from os import listdir
from os.path import isfile, join

substat = {
    "type" : 0,
    "value" : 1,
    "data" : 2
}

data = {
    "sub1" : 0,
    "sub2" : 3,
    "sub3" : 6,
    "sub4" : 9,
    "id" : 13,
    "isAncient" : 19,
    "currentEff" : 20,
    "set" : 21,
    "slot" : 22,
    "grade" : 23, # hopefully this is all 6* now
    "level" : 24,
    "mainStat" : 25,
    "mainValue" : 26,
    "innateStat" : 27, # ungrindable
    "innateValue" : 28, # ungrindable
    "quality" : 41,
    "maxEff" : 42
}

maxRoll = {
    "HP%": 8.0,
    "ATK%": 8.0,
    "DEF%": 8.0,
    "SPD": 6.0,
    "HP flat": 375.0,
    "DEF flat": 20.0,
    "ATK flat": 20.0,
    "CDmg": 7.0,
    "CRate": 6.0,
    "ACC": 8.0,
    "RES": 8.0
}

# legend, purple
maxGrind = {
    "HP%": [10.0, 7.0],
    "ATK%": [10.0, 7.0],
    "DEF%": [10.0, 7.0],
    "SPD": [5.0, 4.0],
    "HP flat": [550, 430],
    "DEF flat": [30.0, 22.0],
    "ATK flat": [30.0, 22.0],
    "CDmg": [0, 0],
    "CRate": [0, 0],
    "ACC": [0, 0],
    "RES": [0, 0]
}

#if (len(sys.argv) == 1 or sys.argv[1] == 'default'):
    #dirname = os.path.dirname(__file__)
    #filename = "runes-data.csv"
    #filepath = os.path.join(dirname, 'Summoners War Exporter Files/')
    #for f in listdir(filepath):
    #    if (isfile(join(filepath, f))):
    #        if (f == "runes-data.csv"):
    #            filename = os.path.join(filepath, f)
    
#else:
    #filename = sys.argv[1]
    #if (not isfile(filename)):
    #    # if not in immediate directory
    #    filename = os.path.join(__file__, filename)
    #    if (not isfile(filename)):
    #        print("Not a file")
    #        exit()

#s1_t;s1_v;s1_data;s2_t;s2_v;s2_data;s3_t;s3_v;s3_data;s4_t;s4_v;s4_data;DT_RowId;
#id;unique_id;monster;originID;monster_n;originName;ancient;efficiency;set;slot;grade;level;
#m_t;m_v;i_t;i_v;locked;sub_res;sub_cdmg;sub_atkf;sub_acc;sub_atkp;sub_defp;sub_deff;sub_hpp;
#sub_hpf;sub_spd;sub_crate;quality;max_efficiency

# logically in order to calculate...
# max efficiency grinded = replace all grinds with max values
# max efficiency no grinds = replace all grinds with 0 
# efficiency differential = (max efficiency grinded - current efficiency)

def round_up(number, decimals):
    if decimals==0:
        return math.ceil(number)
    
    factor = 10 ** decimals
    return math.ceil(number * factor) / factor

def getMinEff(data):
    return float(data["minEff"])

def getMaxEff(data, grindLevel):
    if (grindLevel == -1):
        return float(data["maxEff"])

    if (grindLevel == 1):
        return float(data["maxEffLegend"])
    else:
        return float(data["maxEffPurple"])

def getDifferential(data, grindLevel):
    if (grindLevel == -1):
        return float(data["differential"])

    if (grindLevel == 1):
        return float(data["legend_differential"])
    else:
        return float(data["purple_differential"])
    

def getCurrentEff(data):
    return float(data["runeCurrentEff"])

runes = []

# runeType, substat must be provided to generate a specific set
# no reason to not anyways - grinds are for a specific set and substat
# "All" can and should be used for immemorials
# rune substats that are grindable: spd, atk+, hp+, def+, hp%, def%, atk%
# have placeholders for ancient runes
def specificSubstatGenerate(filename, runeTypeGrind, minRuneEff, substat, grindLevel=1, isGenAncient=False):
    # output runes in array format
    # this way printing it out should be as simple as sort and then output values
    specificRunes = []
    # this would re-read the file in.
    # there's probably a better way to do this
    # TODO: figure out a better way to do this
    with open(filename) as f:
        reader = csv.reader(f, delimiter = ';')
        next(reader)
        for row in reader:
            
            runeSet = row[data.get("set")]

            # if the rune type doesn't match skip
            if (runeTypeGrind != "All" and runeSet != runeTypeGrind):
                continue

            runeMainStat = row[data.get("mainStat")]
            runeMainValue = row[data.get("mainValue")]
            runeCurrentEff = row[data.get("currentEff")]

            # if the rune is below the current min eff skip
            if (minRuneEff > float(runeCurrentEff)):
                continue

            total_calc_eff = 0.00
            total_calc_zero_grinds = 0.00
            total_calc_max_grinds = 0.00
            
            # throw out odd cases i dont feel like handling cause they're not useful
            grade = int(row[data.get("grade")])
            level = int(row[data.get("level")])
            # throw out runes as well unless selected later
            ancient = row[data.get("isAncient")] == "true"
            if (grade < 6 or level < 12):
                continue
            # throw out ancient runes if not specifically optimized for
            if (ancient and not isGenAncient):
                continue

            subs = []
            for i in range(0, 4):
                sub = {}
                index = i * 3
                subType = row[index] 
                subValue = row[index + 1]
                
                if subType != "":
                    
                    # get the grind value
                    grindData = row[index + 2]
                    # technically this also has an enchanted field if we want to do gem stuff later
                    # spoiler: we don't yet
                    # TODO: Implement gems.
                    getData = json.loads(grindData)

                    totalGrinded = getData["gvalue"]
                    
                    runeMaxGrind = maxGrind.get(subType)[0] if grindLevel == 1 else maxGrind.get(subType)[1]

                    sub['type'] = subType
                    sub['value'] = subValue
                    sub['grind'] = totalGrinded

                    # if the rune is not the correct type then ignore grinds completely
                    if substat == subType:
                        rvMin = float(subValue) - totalGrinded
                        rvMax = (rvMin + runeMaxGrind)
                    else:
                        rvMin = float(subValue)
                        rvMax = float(subValue)

                    calc_eff = float(subValue) / (maxRoll[subType] * 5)
                    calcMin = rvMin / (maxRoll[subType] * 5)
                    calcMax = rvMax / (maxRoll[subType] * 5)
                    

                    if subType == "ATK flat" or subType == "DEF flat" or subType == "HP flat":
                        calc_eff /= 2
                        calcMin /= 2
                        calcMax /= 2
                    
                    total_calc_eff += calc_eff
                    total_calc_zero_grinds += calcMin
                    total_calc_max_grinds += calcMax
                    
                # end if
                # add this substat to the substat list
                subs.append(sub)

            # end substats
            # begin innates
            innate = row[data.get("innateStat")]
            innateVal = 0
            if innate != "":
                innateVal = row[data.get("innateValue")]
                calc_innate = float(innateVal) / (maxRoll[innate] * 5)
                if innate == "ATK flat" or innate == "DEF flat" or innate == "HP flat":
                    calc_innate /= 2
                total_calc_eff += calc_innate
                total_calc_max_grinds += calc_innate
                total_calc_zero_grinds += calc_innate


            total_calc_eff = ((total_calc_eff + 1) / 2.8) * 100
            total_min_eff = ((total_calc_zero_grinds + 1) / 2.8) * 100
            total_max_eff = ((total_calc_max_grinds + 1) / 2.8) * 100
            

            display_total_calc_eff = round(total_calc_eff, 2)
            displayMax = round(total_max_eff, 2)
            displayMin = round(total_min_eff, 2)
            differential = round(displayMax - display_total_calc_eff, 2)
            
            # end substats
            # build a rune!
            rune = {
                "runeSet": runeSet,
                "runeMainStat": runeMainStat,
                "runeMainValue": runeMainValue,
                "runeCurrentEff": display_total_calc_eff,
                "slot": row[data.get("slot")],
                "minEff": displayMin,
                "maxEff": displayMax,
                "differential": differential,
                "innate": {
                    "type": innate,
                    "value": innateVal
                }
            }

            for i in range(0, 4):
                hasData = len(subs[i]) != 0
                rune['type' + str(i)] = subs[i]['type'] if hasData else ""
                rune['value' + str(i)] = subs[i]['value'] if hasData else ""
                rune['grind' + str(i)] = subs[i]['grind'] if hasData else ""

            # add to array
            specificRunes.append(rune)

    return specificRunes

# runes is the rune array
# sort is what we're sorting by
# numRunes is how many runes to output
def outputRunes(runes, sort, numRunes):

    # pre sort by the tiebreaker to get correct ordering
    if (sort != 1):
        sortFunction = lambda diff: round_up(getMaxEff(diff, -1), 1)
    else:
        sortFunction = lambda diff: round_up(getDifferential(diff, -1), 1)

    # tiebreaker: max eff if not max eff primary, potential gains otherwise
    firstSortRunes = sorted(runes, key = sortFunction, reverse = True)

    if (sort == 0):
        sortFunction = getCurrentEff
    elif (sort == 1):
        sortFunction = lambda diff: round_up(getMaxEff(diff, -1), 1)
    elif (sort == 2):
        sortFunction = getMinEff
    elif (sort == 3 or sort == 4):
        sortFunction = lambda diff: round_up(getDifferential(diff, -1), 1)

    runesList = sorted(firstSortRunes, key = sortFunction, reverse = True)

    if (len(runesList) == 0):
        print("No runes found.")
        numRunes = 0
    elif (numRunes > len(runesList)):
        print("***Warning: Number of runes less than rune amount selected.")
        numRunes = len(runesList)
    
    # since we only have runes of relevance we can just loop
    for i in range(0, numRunes):
        currentRune = runesList[i]

        firstpart = currentRune["runeSet"] + " S" + currentRune["slot"] + " " + currentRune["runeMainStat"] + ": " + currentRune["runeMainValue"] 
        out = '{:26s}'.format(firstpart)

        out +=  "| Current Efficiency: " + "{:6.2f}".format(currentRune["runeCurrentEff"])
        out += " | Max Efficiency: " + "{:6.2f}".format(currentRune["maxEff"]) + " | Min Efficiency: " + "{:6.2f}".format(currentRune["minEff"]) + "   | Potential Gain: " + "{:6.2f}".format(currentRune["differential"])
        print(out)

        out = ""
        innateType = currentRune["innate"]["type"]
        if (innateType == ""):
            outStr = "No innate."
        else:
            outStr = "Innate " + innateType + ": " + (currentRune["innate"]["value"])
    
        out += '\t'
        out += '{:24s}'.format(outStr)   
        out += " | "

        #print(currentRune)
        for i in range(0, 4):
            subType = currentRune["type"+str(i)]
            subVal = currentRune["value"+str(i)]
            subGrind = currentRune["grind"+str(i)]

            if (subType == ""):
                out += "No sub " + i + "."
            elif maxGrind[subType][0] == 0:
                outStr = subType + ": " + str(subVal)
                out += '{:24s}'.format(outStr)
            else:
                outStr = subType + ": " + str(subVal) + " (" + str(subGrind) + " grind)"
                out += '{:24s}'.format(outStr)
            out += " | "
        print(out)


def generateRunes(filename):
    with open(filename) as f:
        reader = csv.reader(f, delimiter = ';')
        next(reader)

        for row in reader:
            
            runeSet = row[data.get("set")]
            runeMainStat = row[data.get("mainStat")]
            runeMainValue = row[data.get("mainValue")]


            # just test for now
            out = ""
            out += runeSet
            out += " "
            out += runeMainStat
            out += " "
            out += runeMainValue
            out += " "
            
            # test calculate eff
            total_calc_eff = 0.00
            # let's experiment with no grinds and max grinds too
            total_calc_zero_grinds = 0.00
            total_calc_max_grinds_legend = 0.00
            total_calc_max_grinds_purple = 0.00

            # throw out odd cases i dont feel like handling cause they're not useful
            grade = int(row[data.get("grade")])
            level = int(row[data.get("level")])
            # throw out ancient runes as well unless selected later
            ancient = row[data.get("isAncient")] == "true"

            # not 6 star runes or not +12 or ancient
            if (grade < 6 or level < 12 or ancient):
                continue

            #print("----")
            subs = []
            for i in range(0, 4):
                sub = {}
                index = i * 3
                runeType = row[index] 
                runeValue = row[index + 1]
                
                if runeType != "":
                    # get the grind value
                    runeData = row[index + 2]
                    # technically this also has an enchanted field if we want to do gem stuff later
                    # spoiler: we don't
                    getData = json.loads(runeData)

                    totalGrinded = getData["gvalue"]
                    
                    runeMaxGrindLegend = maxGrind.get(runeType)[0]
                    runeMaxGrindPurple = maxGrind.get(runeType)[1]

                    sub['type'] = runeType
                    sub['value'] = runeValue
                    sub['grind'] = totalGrinded
                    #print(totalGrinded)
                    #if runeMaxGrind > 0:
                        #print(runeType + " " + runeValue + " (" + str(totalGrinded) + " grinded)")
                    #else:
                        #print(runeType + " " + runeValue)

                    rvMin = float(runeValue) - totalGrinded
                    rvMaxL = rvMin + runeMaxGrindLegend
                    rvMaxP = rvMin + runeMaxGrindPurple

                    calc_eff = float(runeValue) / (maxRoll[runeType] * 5)
                    calcMin = rvMin / (maxRoll[runeType] * 5)
                    calcMaxL = rvMaxL / (maxRoll[runeType] * 5)
                    calcMaxP = rvMaxP / (maxRoll[runeType] * 5)

                    if runeType == "ATK flat" or runeType == "DEF flat" or runeType == "HP flat":
                        calc_eff /= 2
                        calcMin /= 2
                        calcMaxL /= 2
                        calcMaxP /= 2
                    
                    total_calc_eff += calc_eff
                    total_calc_zero_grinds += calcMin
                    total_calc_max_grinds_legend += calcMaxL
                    total_calc_max_grinds_purple += calcMaxP
                # end if
                # add this substat to the substat list
                subs.append(sub)

            #print(subs)
            
            innate = row[data.get("innateStat")]
            innateVal = 0
            if innate != "":
                innateVal = row[data.get("innateValue")]
                calc_innate = float(innateVal) / (maxRoll[innate] * 5)
                if innate == "ATK flat" or innate == "DEF flat" or innate == "HP flat":
                    calc_innate /= 2
                total_calc_eff += calc_innate
                total_calc_max_grinds_legend += calc_innate
                total_calc_max_grinds_purple += calc_innate
                total_calc_zero_grinds += calc_innate


            total_calc_eff = ((total_calc_eff + 1) / 2.8) * 100
            total_min_eff = ((total_calc_zero_grinds + 1) / 2.8) * 100
            total_max_eff_legend = ((total_calc_max_grinds_legend + 1) / 2.8) * 100
            total_max_eff_purple = ((total_calc_max_grinds_purple + 1) / 2.8) * 100

            display_total_calc_eff = round(total_calc_eff, 2)
            displayMaxL = round(total_max_eff_legend, 2)
            displayMaxP = round(total_max_eff_purple, 2)
            displayMin = round(total_min_eff, 2)
            effDifferentialLegend = round(displayMaxL - display_total_calc_eff, 2)
            effDifferentialPurple = round(displayMaxP - display_total_calc_eff, 2)
        
            out = out + "| Current eff: " + str(display_total_calc_eff) + " | Min Eff: " + str(displayMin) + " | Max Eff Legend: " + str(displayMaxL) + " | Max Eff Purple: " + str(displayMaxP) + " | Potential Gain: " + str(effDifferentialLegend)

            #print(out)

            # document in the infinity rune matrix

            rune = {
                "runeSet": runeSet,
                "runeMainStat": runeMainStat,
                "runeMainValue": runeMainValue,
                "runeCurrentEff": display_total_calc_eff,
                "slot": row[data.get("slot")],
                "minEff": displayMin,
                "maxEffLegend": displayMaxL,
                "maxEffPurple": displayMaxP,
                "legend_differential": effDifferentialLegend,
                "purple_differential": effDifferentialPurple,
                "innate": {
                    "type": innate,
                    "value": innateVal
                }
            }

            for i in range(0, 4):
                hasData = len(subs[i]) != 0
                rune['type' + str(i)] = subs[i]['type'] if hasData else ""
                rune['value' + str(i)] = subs[i]['value'] if hasData else ""
                rune['grind' + str(i)] = subs[i]['grind'] if hasData else ""
            

            #print(rune)
            runes.append(rune)

# sort = an integer representing what to sort by
# runeType = a string representing runes
# numRunes = number of runes to display
# minRuneEff = minimum rune efficiency for runes
def outputData(sort, runeType="All", numRunes=10, minRuneEff=0.0, grindLevel=1):
    numRunePrinted = 0
    itr = 0

    print("\nSearch Results:")
    while (numRunePrinted < numRunes):
        # don't crash printing too many
        if len(runeList) <= itr:
            break
        
        currentRune = runeList[itr]
        # increment iterator
        itr += 1

        if (runeType != "All"):
            if currentRune["runeSet"] != runeType:
                # rune doesn't match type selected
                # go next
                continue
        if ((currentRune["runeCurrentEff"]) < minRuneEff):
            # rune below min eff standards
            # go next
            continue

        maxEff = 0.0
        potentialDiff = 0.0
        # if legend
        if (grindLevel == 1):
            maxEff = currentRune["maxEffLegend"]
            potentialDiff = currentRune["legend_differential"]
        else:
            maxEff = currentRune["maxEffPurple"]
            potentialDiff = currentRune["purple_differential"]
        
        firstpart = currentRune["runeSet"] + " S" + currentRune["slot"] + " " + currentRune["runeMainStat"] + ": " + currentRune["runeMainValue"] 
        out = '{:26s}'.format(firstpart)

        out +=  "| Current Efficiency: " + "{:6.2f}".format(currentRune["runeCurrentEff"])
        out += " | Max Efficiency: " + "{:6.2f}".format(maxEff) + " | Min Efficiency: " + "{:6.2f}".format(currentRune["minEff"]) + "   | Potential Gain: " + "{:6.2f}".format(potentialDiff)
        print(out)

        out = ""
        innateType = currentRune["innate"]["type"]
        if (innateType == ""):
            outStr = "No innate."
        else:
            outStr = "Innate " + innateType + ": " + (currentRune["innate"]["value"])
    
        out += '\t'
        out += '{:24s}'.format(outStr)   
        numRunePrinted += 1
        out += " | "

        #print(currentRune)
        for i in range(0, 4):
            subType = currentRune["type"+str(i)]
            subVal = currentRune["value"+str(i)]
            subGrind = currentRune["grind"+str(i)]

            if (subType == ""):
                out += "No sub " + i + "."
            elif maxGrind[subType][grindLevel] == 0:
                outStr = subType + ": " + str(subVal)
                out += '{:24s}'.format(outStr)
            else:
                outStr = subType + ": " + str(subVal) + " (" + str(subGrind) + " grind)"
                out += '{:24s}'.format(outStr)
            out += " | "
        print(out)

    print("----")


# if run as a standalone
if __name__ == "__main__":

    print("----\nRune Grinding Aide Tool v1.0\n----")

    if (len(sys.argv) > 1):
        print(sys.argv[1][-4:])

    dirname = os.path.dirname(__file__)

    filename = os.path.join(dirname, "runes-data.csv")

    print (filename)

    if (len(sys.argv) > 1 and sys.argv[1][-4:] == ".csv"):
        filename = sys.argv[1]
        if (not isfile(filename)):
            # if not in immediate directory
            filename = os.path.join(dirname, filename)
            # check the long path
            if (not isfile(filename)):
                # check the subdirectory
                filename = os.path.join(dirname, "input\\" + sys.argv[1])
                print(filename)
                if (not isfile(filename)):
                    print("Not a file")
                    exit()
    else:
        # if arguments aren't correct or don't contain the correct data
        filename = "runes-data.csv"
        if (not isfile(filename)):
            # if not in immediate directory
            filename = os.path.join(dirname, filename)
            if (not isfile(filename)):
                filename = os.path.join(dirname, "input\\" + "runes-data.csv")
                print(filename)
                if (not isfile(filename)):
                    print("Not a file")
                    exit()
    generateRunes(filename)

    # conditions should be added here later
    while True:
        sort = -1
        while (sort == -1):
            inData = input("What do you want to sort your runes by?\n0: Current Efficiency\n1: Max Grinded Efficiency\n2: Zero Grind Efficiency\n3: Potential Efficiency Gains\n4: Specific Grind Gains\nInput: ")
            try:
                sortNum = int(inData)
                if (sortNum > -1 and sortNum < 5):
                    sort = sortNum
                else:
                    print("Enter a number from 0-4.")

            except ValueError:
                # if the number entered was NaN or otherwise could not convert
                print("Enter a number from 0-4.")

        allTypes = ["All", "Energy", "Guard", "Swift", "Blade", "Rage", "Focus", "Endure", "Fatal", "Despair", "Vampire", "Violent", "Nemesis", "Will", "Shield", "Revenge", "Destroy", "Fight", "Determination", "Enhance", "Accuracy", "Tolerance"]
        runeType = ""
        while (runeType == ""):
            inData = input("What type of runes do you want to sort by? (enter All or input nothing for all, default=All) ").capitalize()
            # common shorthands
            if (inData == "Vio"):
                inData = "Violent"
            if (inData == "Rev"):
                inData = "Revenge"
            if (inData == "Nem"):
                inData = "Nemesis"
            if (inData == "Vamp"):
                inData = "Vampire"
            # if they picked a real set
            if (inData in allTypes):
                runeType = inData
            # if they input nothing
            if (inData == ""):
                runeType = "All"
            # if they didn't put anything valid in
            if (runeType == ""):
                print("Please enter a valid rune type.")
        
        numRunes = 0
        inData = input("How many runes to get? (Default=10) ")
        try:
            numRunes = int(inData)
        except ValueError:
            # if the number entered was NaN or otherwise could not convert
            numRunes = 10

        minRuneEff = 0.0
        inData = input("Minimum current efficiency? (Default=none) ")
        try:
            minRuneEff = float(inData)
        except ValueError:
            # if the number entered was NaN or otherwise could not convert
            minRuneEff = 0.0

        grindLevel = 1
        inData = input("Select grind level:\n0: Purple\n1: Legend\nInput: (default=legend) ")
        try:
            inputNum = int(inData)
            # just use legend if user is dumb and puts bad values
            if (grindLevel > 1 or grindLevel < 0):
                grindLevel = 1
            else:
                grindLevel = inputNum
        except ValueError:
            grindLevel = 1

        #print("Input Result: " + str(grindLevel))
        
        if (sort < 4):

            if (sort != 1):
                runeList = sorted(runes, key=lambda mEff: getMaxEff(mEff, grindLevel), reverse=True)
            else:
                runeList = sorted(runes, key=lambda diff: getDifferential(diff, grindLevel), reverse=True)

            if (sort == 0):
                runeList = sorted(runes, key=getCurrentEff, reverse=True)
            elif (sort == 1):
                runeList = sorted(runes, key=lambda mEff: getMaxEff(mEff, grindLevel), reverse=True)
            elif (sort == 2):
                runeList = sorted(runes, key=getMinEff, reverse=True)
            elif (sort == 3):
                runeList = sorted(runes, key=lambda diff: getDifferential(diff, grindLevel), reverse=True)

            outputData(sort, runeType, numRunes, minRuneEff, grindLevel)
        
        else:
            allGrindables = ["SPD", "HP flat", "DEF flat", "ATK flat", "ATK%", "DEF%", "HP%"]
            grindable = ""
            while (grindable == ""): 
                inData = input("Enter the stat you'd like to grind:\nYou can use flat stats by saying 'stat flat' or 'stat+'.\nUse 'stat%' for percent stats.\nInput: ")
                # go through the order of things that would need to be fixed
                # 1: accidental spd+ 
                inData.replace("SPD+", "SPD") 
                # 2: using + instead of ' flat'
                # 3: capitalization
                inData.replace("Flat", "flat")
                inData.replace("+", " flat")
                
                inData.replace("hp", "HP")
                inData.replace("atk", "ATK")
                inData.replace("def", "DEF")

                if (inData in allGrindables):
                    grindable = inData
                
                if grindable == "":
                    print("Please enter a valid grindable stat.")
            
            if (sort == 4):
                runeList = specificSubstatGenerate(filename, runeType, minRuneEff, grindable, grindLevel, False)
                outputRunes(runeList, sort, numRunes)
                print("----")

        
