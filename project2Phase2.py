
def extractCityStateNames(line):
    pieces = line.split(",")
    return pieces[0] + pieces[1][:3]

def extractCoordinates(line):
    pieces = line.split(",")
    return [int(pieces[1].split("[")[1]), int(pieces[2].split("]")[0])]

def extractPopulation(line):
    pieces = line.split(",")
    return int(pieces[2].split("]")[1])


def loadData():
    f = open("miles.txt")
    
    # The dictionary that will hold all the city information
    cityDataDict = {}
    
    # Tracks which city we are currently processing
    cityIndex = 0
    
    # Keeps track of the list of all city/state names
    cityStateNamesList = []
    
    # Reads from the file, one line at a time
    for line in f:
        
        # Checks if the line is a "city line", i.e., contains information about
        # the city
        if line[0].isalpha():
                            
            cityStateName = extractCityStateNames(line)
            coords = extractCoordinates(line)
            pop = extractPopulation(line)         
            cityDataDict[cityStateName] = [coords, pop, {}]            
            cityStateNamesList.append(cityStateName)
            index = -2
            cityIndex = cityIndex + 1
        
        # Checks if the line is a "distance line", i.e., contains information
        # distances from this city to previous cities            
        elif line[0].isdigit():
            distancesInThisLine = [int(x) for x in line.split()]
            
            for i in range(len(distancesInThisLine)):
                destinationCity = cityStateNamesList[index]
                index = index - 1
                cityDataDict[cityStateName][2][destinationCity] = distancesInThisLine[i]
                cityDataDict[destinationCity][2][cityStateName] = distancesInThisLine[i]
    
    return cityDataDict
            
def getCoordinates(cityDataDict, cityName):
    if cityName in cityDataDict:
        return cityDataDict[cityName][0]
    else:
        return None

def getPopulation(cityDataDict, cityName):
    if cityName in cityDataDict:
        return cityDataDict[cityName][1]  
    else:
        return None
   
def getDistance(cityDataDict, cityName1, cityName2):
    if (cityName1 in cityDataDict) and (cityName2 in cityDataDict):
        if (cityName1 != cityName2):
            return cityDataDict[cityName1][2][cityName2]
        else:
            return 0
    else:
        return None

def nearbyCities(cityDataDict, cityName, r):
    if cityName not in cityDataDict:
        return None
    
    nearbyCityList = [cityName]
    for city in cityDataDict:
        if (city != cityName) and (cityDataDict[cityName][2][city] <= r):
            nearbyCityList.append(city)

    return nearbyCityList

def numNotserved(served, cityDataDictionary, name, r) :    
    allCitySet = set(cityDataDictionary.keys())
    notServedSet = allCitySet - served
    return len(notServedSet & set(nearbyCities(cityDataDictionary, name, r)))

def nextFacility(served, cityDataDictionary, r) :

    facility = None      # Name of city that will be the next service facility
    numberServed = 0     # Number of cities that facility will serve

    cityList = sorted(list(cityDataDictionary.keys()))

    # For each city
    for c in cityList:
        # compute how many unserved cities will be served by city c
        willBeServed = numNotserved(served, cityDataDictionary, c, r)
        if (willBeServed > 0):
            print(c, willBeServed)
        
        # if it can serve more cities than the previous best city
        if willBeServed >  numberServed:
            # make it the service center
            facility = c
            numberServed = willBeServed
            
    print("**********************")
    print("Picked: ", facility)
    print("**********************")
    
    return facility

def greedyFacilitySet(cityDataDictionary, r) :
    print("**********************")
    
    # Set of cities that are served by current facilities
    served = set()

    # List of cities that are at which facilities are located
    facilities = []

    # Get the city that is the next best service facility
    facility = nextFacility(served, cityDataDictionary, r )

    # While there are more cities to be served
    while facility :

        # Mark each city as served that will be served by this facility
        newlyServed = set(nearbyCities(cityDataDictionary, facility, r))
        served |= newlyServed

        # Append the city to the list of service facilities
        facilities.append(facility)

        # Get the city that is the next best service facility
        facility = nextFacility(served, cityDataDictionary, r)

    return facilities

def feasible(cityDataDictionary, facilityList, r):
    coveredCities = set()
    for cityName in facilityList:
        coveredCities |= set(nearbyCities(cityDataDictionary, cityName, r))
        
    return len(coveredCities) == 128

def firstFeasible(cityDataDictionary, listFacilityLists, r):
    for facilityList in listFacilityLists:
        if feasible(cityDataDictionary, facilityList, r):
            return facilityList
    return []


def bruteForceFacilityLocation(cityDataDictionary, cityList, r, k):
    
    # Base cases
    if k == 0:
        return [[], [[]]]
    
    if len(cityList) == k:
        if feasible(cityDataDictionary, cityList, r):
            return [cityList, [cityList]]
        else:
            return [[], [cityList]]
    
    # Recursive case
    L = bruteForceFacilityLocation(cityDataDictionary, cityList[1:], r, k-1)
    if L[0] != []:
        return L
    else:
        L[1] = [[cityList[0]] + elem for elem in L[1]]
        L[0] = firstFeasible(cityDataDictionary, L[1], r)
        if L[0] != []:
            return L
        
    LL = bruteForceFacilityLocation(cityDataDictionary, cityList[1:], r, k)
    if LL[0] != []:
        return LL
    else:
        L[1].extend(LL[1])
        return L
    
def optimalFacilitySet(cityDataDictionary, r, oneSolution):
    cityList = list(cityDataDictionary.keys())
    return bruteForceFacilityLocation(cityDataDictionary, cityList, r, len(oneSolution)-1)[0]
