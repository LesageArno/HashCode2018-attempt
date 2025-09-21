### Libraries ---------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import time




### File Selection ----------------------------------------------------------------------------------------------------
# a_example.in, b_should_be_easy.in, c_no_hurry.in, d_metropolis.in, e_high_bonus.in
#FILE = "a_example.in"
#FILE = "b_should_be_easy.in"
#FILE = "c_no_hurry.in"
#FILE = "d_metropolis.in"
FILE = "e_high_bonus.in"




### Table creation and Information retrievial -------------------------------------------------------------------------
## Grid Information
with open(f"instances-HashCode-2018\\{FILE}", "r") as file:
    nRow, nCol, fleetSize, nRide, preRideBonus, nStep = [int(i) for i in file.readline().split()]
print(nRow, nCol, fleetSize, nRide, preRideBonus, nStep)


## Create ride table and retrieve information
ridesInfo = pd.read_table(f"instances-HashCode-2018\\{FILE}", sep=" ", skiprows=1, header=None, dtype=int, 
    names=["startRow","startCol","endRow","endCol","earliestStart","latestEnd"]
)

# Compute Manhattan distance for the ride and from the origin
ridesInfo["Manhattan"] = (ridesInfo["startCol"] - ridesInfo["endCol"]).abs() + (ridesInfo["startRow"] - ridesInfo["endRow"]).abs()
ridesInfo["ManhattanFromOrigin"] = ridesInfo["startCol"] + ridesInfo["startRow"]

# Remove the ride which cannot be completed due to latest end being too early
ridesInfo = ridesInfo[(ridesInfo["ManhattanFromOrigin"]+ridesInfo["Manhattan"] <= ridesInfo["latestEnd"])]

# Sort rides by earliest start
ridesInfo.sort_values("earliestStart", inplace=True)


## Create fleet table and initialise it
fleetInfo = pd.DataFrame(columns=["xBeforeMove", "yBeforeMove"])
fleetInfo["xBeforeMove"] = np.zeros(fleetSize, dtype=int)
fleetInfo["yBeforeMove"] = np.zeros(fleetSize, dtype=int)

# Add attributes riding and currentRide to the fleet table, the first rides are the one starting early
fleetInfo["riding"] = np.zeros(fleetSize, dtype=bool)
fleetInfo["currentRide"] = ridesInfo.head(fleetSize).index.copy(deep=True)


## Join the tables
fleetInfo = fleetInfo.join(ridesInfo[["earliestStart", "startCol","startRow","endCol","endRow","Manhattan"]], "currentRide")
fleetInfo["timeRemainingBeforeNextPos"] = ridesInfo.head(fleetSize)["ManhattanFromOrigin"].to_numpy()

# Keep track of the rides taken
proceededRides = {i:list() for i in range(fleetSize)}


# Drop unused informations and rides already taken
ridesInfo.drop(index=fleetInfo["currentRide"], inplace=True)
ridesInfo.drop(columns="ManhattanFromOrigin")




### Function attributing rides via side-effect ------------------------------------------------------------------------
def attributeNearestRide(ridesInfo:pd.DataFrame, fleetInfo:pd.DataFrame, condition, step:int = 0):
    # Update to the new position
    fleetInfo.loc[condition, "xBeforeMove"] = fleetInfo.loc[condition, "endRow"].to_numpy()
    fleetInfo.loc[condition, "yBeforeMove"] = fleetInfo.loc[condition, "endCol"].to_numpy()
    
    # Attribute rides for each vehicule not having rides and not going to a ride currently
    for vehiculeInfo in fleetInfo.loc[condition, ["xBeforeMove", "yBeforeMove"]].itertuples():
        
        # Manhattan taking into account the emergency of the ride 
        modifiedManhattan = (ridesInfo.startRow - vehiculeInfo.xBeforeMove).abs() + (ridesInfo.startCol - vehiculeInfo.yBeforeMove).abs() + ridesInfo["earliestStart"] - step
        
        # Attribute the closest ride in term of this distance
        rideIndex = modifiedManhattan.sort_values().index[0]
        
        # Modify fleet information
        fleetInfo.loc[vehiculeInfo.Index, "currentRide"] = rideIndex
        fleetInfo.loc[vehiculeInfo.Index, ["earliestStart", "startCol", "startRow", "endCol", "endRow", "Manhattan"]] = ridesInfo.loc[rideIndex,["earliestStart", "startCol", "startRow", "endCol", "endRow", "Manhattan"]].copy(deep=True).to_numpy()
        fleetInfo.loc[vehiculeInfo.Index, "timeRemainingBeforeNextPos"] = modifiedManhattan[rideIndex] - ridesInfo.loc[rideIndex, "earliestStart"] + step
        fleetInfo.loc[vehiculeInfo.Index, "riding"] = False
        
        # Remove rides which are taken
        ridesInfo.drop(index=rideIndex, inplace=True)




### Main Loop ---------------------------------------------------------------------------------------------------------
ridesRemaining = True
begin = time.time()

# For each step
for step in range(nStep):
    
    # Check if rides are remaining
    if ridesRemaining and ridesInfo.shape[0] == 0:
        ridesRemaining = False
    
    # Drop unfeasable rides (cannot be achieved within remaining step or below latestEnd)
    if ridesRemaining:
        condition = (ridesInfo["Manhattan"] > nStep-step) | ridesInfo["Manhattan"] + step > ridesInfo["latestEnd"]
        ridesInfo.drop(index=ridesInfo[condition].index, inplace=True)
    
    
    ## Logic to start a ride when arrived at the destination
    # Check for vehicule being at the starting point of their rides and at the right time
    condition = (fleetInfo["timeRemainingBeforeNextPos"]<=0) & (fleetInfo["riding"]==False) & (fleetInfo["earliestStart"] <= step)
    
    # Make these vehicules start ride
    fleetInfo.loc[condition, "timeRemainingBeforeNextPos"] = fleetInfo.loc[condition, "Manhattan"].to_numpy()
    fleetInfo.loc[condition, "xBeforeMove"] = fleetInfo.loc[condition, "startRow"].to_numpy()
    fleetInfo.loc[condition, "yBeforeMove"] = fleetInfo.loc[condition, "startCol"].to_numpy()
    fleetInfo.loc[condition, "riding"] = True
    

    ## Logic to end the ride when arrived at the destination
    # Check for vehicules which finish their rides
    condition = (fleetInfo["timeRemainingBeforeNextPos"]<=0) & (fleetInfo["riding"]==True)
    
    # Store the proceeded rides for each vehicules
    for vehicule, ride in zip(fleetInfo.loc[condition, "currentRide"].index.tolist(),fleetInfo.loc[condition, "currentRide"].to_numpy().tolist()):
        proceededRides[vehicule] = list(set(proceededRides[vehicule] + [ride]))
    
    # If some rides are remaining, attribute them
    if ridesRemaining:
        attributeNearestRide(ridesInfo, fleetInfo, condition, step)

    # Update the remaining time to next destionation
    fleetInfo["timeRemainingBeforeNextPos"] -= 1

    # Update user
    if not (step % 1000):
        print(f"{step}: {time.time()-begin:.6}s")
   
        
        

### Save output file --------------------------------------------------------------------------------------------------
with open(f"results\\{FILE}"[:-3]+".out", "w") as file:
    for key, value in proceededRides.items():
        file.write(f"{key+1} " + " ".join([str(i) for i in set(value)]) +"\n")
