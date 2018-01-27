"""
Translated from: https://github.com/hansukyang/UWG_Matlab/blob/master/readDOE.m
Translated to Python by Saeran Vasanthakumar (saeranv@gmail.com) - April, 2017
"""

import sys
import os
import cPickle

from building import Building
from material import Material
from element import Element
from BEMDef import BEMDef
from schdef import SchDef
from utilities import read_csv, str2fl
import utilities
import pprint
from decimal import Decimal

DIR_UP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIR_DOE_PATH = os.path.join(DIR_UP_PATH,"resources","DOERefBuildings")

def readDOE(serialize_output=True):
    """
    Read csv files of DOE buildings
    Sheet 1 = BuildingSummary
    Sheet 2 = ZoneSummary
    Sheet 3 = LocationSummary
    Sheet 4 = Schedules
    Note BLD8 & 10 = school


    Then make matrix of ref data as nested nested lists [16, 3, 16]:
    matrix refDOE = Building objs
    matrix Schedule = SchDef objs
    matrix refBEM (16,3,16) = BEMDef
    where:
        [16,3,16] is Type = 1-16, Era = 1-3, climate zone = 1-16
        i.e.
        Type: FullServiceRestaurant, Era: Pre80, Zone: 6A Minneapolis
    Nested tree:
    [TYPE_1:
        ERA_1:
            CLIMATE_ZONE_1
            ...
            CLIMATE_ZONE_16
        ERA_2:
            CLIMATE_ZONE_1
            ...
            CLIMATE_ZONE_16
        ...
        ERA_3:
            CLIMATE_ZONE_1
            ...
            CLIMATE_ZONE_16]

    """

    #Define constants
    # DOE Building Types
    bldType = [
        'FullServiceRestaurant',    # 1
        'Hospital',                 # 2
        'LargeHotel',               # 3
        'LargeOffice',              # 4
        'MedOffice',                # 5
        'MidRiseApartment',         # 6
        'OutPatient',               # 7
        'PrimarySchool',            # 8
        'QuickServiceRestaurant',   # 9
        'SecondarySchool',          # 10
        'SmallHotel',               # 11
        'SmallOffice',              # 12
        'StandAloneRetail',         # 13
        'StripMall',                # 14
        'SuperMarket',              # 15
        'WareHouse']                # 16

    builtEra = [
        'Pre80',                    # 1
        'Pst80',                    # 2
        'New'                       # 3
        ]

    zoneType = [
        '1A (Miami)',               # 1
        '2A (Houston)',             # 2
        '2B (Phoenix)',             # 3
        '3A (Atlanta)',             # 4
        '3B-CA (Los Angeles)',      # 5
        '3B (Las Vegas)',           # 6
        '3C (San Francisco)',       # 7
        '4A (Baltimore)',           # 8
        '4B (Albuquerque)',         # 9
        '4C (Seattle)',             # 10
        '5A (Chicago)',             # 11
        '5B (Boulder)',             # 12
        '6A (Minneapolis)',         # 13
        '6B (Helena)',              # 14
        '7 (Duluth)',               # 15
        '8 (Fairbanks)'             # 16
        ]


    #Nested, nested lists of Building, SchDef, BEMDef objects
    refDOE = map(lambda j_: map (lambda k_: [None]*16,[None]*3), [None]*16)     #refDOE(16,3,16) = Building;
    Schedule = map(lambda j_: map (lambda k_: [None]*16,[None]*3), [None]*16)   #Schedule (16,3,16) = SchDef;
    refBEM = map(lambda j_: map (lambda k_: [None]*16,[None]*3), [None]*16)     #refBEM (16,3,16) = BEMDef;

    #Purpose: Loop through every DOE reference csv and extract building data
    #Nested loop = 16 types, 3 era, 16 zones = time complexity O(n*m*k) = 768

    for i in xrange(16):
        #print '\tType: ', bldType[i]
        #print '-----i-------'
        #print i+1
        # Read building summary (Sheet 1)
        file_doe_name_bld = os.path.join("{}".format(DIR_DOE_PATH), "BLD{}".format(i+1),"BLD{}_BuildingSummary.csv".format(i+1))
        list_doe1 = read_csv(file_doe_name_bld)
        #listof(listof 3 era values)
        nFloor      = str2fl(list_doe1[3][3:6])      # Number of Floors, this will be list of floats and str if "basement"
        glazing     = str2fl(list_doe1[4][3:6])      # [?] Total
        hCeiling    = str2fl(list_doe1[5][3:6])      # [m] Ceiling height
        ver2hor     = str2fl(list_doe1[7][3:6])      # Wall to Skin Ratio
        AreaRoof    = str2fl(list_doe1[8][3:6])      # [m2] Gross Dimensions - Total area

        # Read zone summary (Sheet 2)
        file_doe_name_zone = os.path.join("{}".format(DIR_DOE_PATH), "BLD{}".format(i+1),"BLD{}_ZoneSummary.csv".format(i+1))
        list_doe2 = read_csv(file_doe_name_zone)
        #listof(listof 3 eras)
        AreaFloor   = str2fl([list_doe2[2][5],list_doe2[3][5],list_doe2[4][5]])       # [m2]
        Volume      = str2fl([list_doe2[2][6],list_doe2[3][6],list_doe2[4][6]])       # [m3]
        AreaWall    = str2fl([list_doe2[2][8],list_doe2[3][8],list_doe2[4][8]])       # [m2]
        AreaWindow  = str2fl([list_doe2[2][9],list_doe2[3][9],list_doe2[4][9]])       # [m2]
        Occupant    = str2fl([list_doe2[2][11],list_doe2[3][11],list_doe2[4][11]])    # Number of People
        Light       = str2fl([list_doe2[2][12],list_doe2[3][12],list_doe2[4][12]])    # [W/m2]
        Elec        = str2fl([list_doe2[2][13],list_doe2[3][13],list_doe2[4][13]])    # [W/m2] Electric Plug and Process
        Gas         = str2fl([list_doe2[2][14],list_doe2[3][14],list_doe2[4][14]])    # [W/m2] Gas Plug and Process
        SHW         = str2fl([list_doe2[2][15],list_doe2[3][15],list_doe2[4][15]])    # [Litres/hr] Peak Service Hot Water
        Vent        = str2fl([list_doe2[2][17],list_doe2[3][17],list_doe2[4][17]])    # [L/s/m2] Ventilation
        Infil       = str2fl([list_doe2[2][20],list_doe2[3][20],list_doe2[4][20]])    # Air Changes Per Hour (ACH) Infiltration

        # Read location summary (Sheet 3)
        file_doe_name_location = os.path.join("{}".format(DIR_DOE_PATH), "BLD{}".format(i+1),"BLD{}_LocationSummary.csv".format(i+1))
        list_doe3 = read_csv(file_doe_name_location)
        #(listof (listof 3 eras (listof 16 climate types)))
        TypeWall    = [list_doe3[3][4:20],list_doe3[14][4:20],list_doe3[25][4:20]]            # Construction type
        RvalWall    = str2fl([list_doe3[4][4:20],list_doe3[15][4:20],list_doe3[26][4:20]])     # [m2*K/W] R-value
        TypeRoof    = [list_doe3[5][4:20],list_doe3[16][4:20],list_doe3[27][4:20]]            # Construction type
        RvalRoof    = str2fl([list_doe3[6][4:20],list_doe3[17][4:20],list_doe3[28][4:20]])     # [m2*K/W] R-value
        Uwindow     = str2fl([list_doe3[7][4:20],list_doe3[18][4:20],list_doe3[29][4:20]])     # [W/m2*K] U-factor
        SHGC        = str2fl([list_doe3[8][4:20],list_doe3[19][4:20],list_doe3[30][4:20]])     # [-] coefficient
        HVAC        = str2fl([list_doe3[9][4:20],list_doe3[20][4:20],list_doe3[31][4:20]])     # [kW] Air Conditioning
        HEAT        = str2fl([list_doe3[10][4:20],list_doe3[21][4:20],list_doe3[32][4:20]])    # [kW] Heating
        COP         = str2fl([list_doe3[11][4:20],list_doe3[22][4:20],list_doe3[33][4:20]])    # [-] Air Conditioning COP
        EffHeat     = str2fl([list_doe3[12][4:20],list_doe3[23][4:20],list_doe3[34][4:20]])    # [%] Heating Efficiency
        FanFlow     = str2fl([list_doe3[13][4:20],list_doe3[24][4:20],list_doe3[35][4:20]])    # [m3/s] Fan Max Flow Rate

        # Read Schedules (Sheet 4)
        file_doe_name_schedules = os.path.join("{}".format(DIR_DOE_PATH), "BLD{}".format(i+1),"BLD{}_Schedules.csv".format(i+1))
        list_doe4 = read_csv(file_doe_name_schedules)

        #listof(listof weekday, sat, sun (list of 24 fractions)))
        SchEquip    = str2fl([list_doe4[1][6:30],list_doe4[2][6:30],list_doe4[3][6:30]])      # Equipment Schedule 24 hrs
        SchLight    = str2fl([list_doe4[4][6:30],list_doe4[5][6:30],list_doe4[6][6:30]])      # Light Schedule 24 hrs; Wkday=Sat=Sun=Hol
        SchOcc      = str2fl([list_doe4[7][6:30],list_doe4[8][6:30],list_doe4[9][6:30]])      # Occupancy Schedule 24 hrs
        SetCool     = str2fl([list_doe4[10][6:30],list_doe4[11][6:30],list_doe4[12][6:30]])   # Cooling Setpoint Schedule 24 hrs
        SetHeat     = str2fl([list_doe4[13][6:30],list_doe4[14][6:30],list_doe4[15][6:30]])   # Heating Setpoint Schedule 24 hrs; summer design
        SchGas      = str2fl([list_doe4[16][6:30],list_doe4[17][6:30],list_doe4[18][6:30]])   # Gas Equipment Schedule 24 hrs; wkday=sat
        SchSWH      = str2fl([list_doe4[19][6:30],list_doe4[20][6:30],list_doe4[21][6:30]])   # Solar Water Heating Schedule 24 hrs; wkday=summerdesign, sat=winterdesgin

        #i = 16 types of buildings
        #print "type: ", bldType[i]
        for j in xrange(3):
            #print '\tera: ', builtEra[j]
            #print '-----j-------'
            #print j+1
            for k in xrange(16):
                #print '\tclimate zone: ', zoneType[k]
                """
                if i==13 and j ==0 and k==6:
                    dd = lambda x: Decimal.from_float(x)
                    print dd(HVAC[j][k])
                    print HVAC[j][k]
                    print dd(AreaFloor[j])
                    print dd(HVAC[j][k]*1000.0/AreaFloor[j])
                """
                B = Building(
                    hCeiling[j],                        # floorHeight by era
                    1,                                  # intHeatNight
                    1,                                  # intHeatDay
                    0.1,                                # intHeatFRad
                    0.1,                                # intHeatFLat
                    Infil[j],                           # infil (ACH) by era
                    Vent[j]/1000,                       # vent (m^3/s/m^2) by era, converted from liters
                    glazing[j],                         # glazing ratio by era
                    Uwindow[j][k],                      # uValue by era, by climate type
                    SHGC[j][k],                         # SHGC, by era, by climate type
                    'AIR',                              # cooling condensation system type: AIR, WATER
                    COP[j][k],                          # cop by era, climate type
                    297,                                # coolSetpointDay = 24 C
                    297,                                # coolSetpointNight
                    293,                                # heatSetpointDay = 20 C
                    293,                                # heatSetpointNight
                    (HVAC[j][k]*1000.0)/AreaFloor[j],   # coolCap converted to W/m2 by era, climate type
                    EffHeat[j][k],                      # heatEff by era, climate type
                    293)                                # initialTemp at 20 C

                #Not defined in the constructor
                B.heatCap = (HEAT[j][k]*1000.0)/AreaFloor[j]         # heating Capacity converted to W/m2 by era, climate type
                B.Type = bldType[i]
                B.Era = builtEra[j]
                B.Zone = zoneType[k]
                refDOE[i][j][k] = B
                #print '\t\t', B

                # Define wall, mass(floor), roof
                # Referece from E+ for conductivity, thickness (reference below)

                # Material: (thermalCond, volHeat = specific heat * density)
                Concrete = Material (1.311, 836.8 * 2240,"Concrete")
                Insulation = Material (0.049, 836.8 * 265.0, "Insulation")
                Gypsum = Material (0.16, 830.0 * 784.9, "Gypsum")
                Wood = Material (0.11, 1210.0 * 544.62, "Wood")
                Stucco = Material(0.6918,  837.0 * 1858.0, "Stucco")

                # Wall (1 in stucco, concrete, insulation, gypsum)
                # Check TypWall by era, by climate
                if TypeWall[j][k] == "MassWall":
                    #Construct wall based on R value of Wall from refDOE and properties defined above
                    # 1" stucco, 8" concrete, tbd insulation, 1/2" gypsum
                    Rbase = 0.271087 # R val based on stucco, concrete, gypsum
                    Rins = RvalWall[j][k] - Rbase #find insulation value
                    D_ins = Rins * Insulation.thermalCond # depth of ins from m2*K/W * W/m*K = m
                    if D_ins > 0.01:
                        thickness = [0.0254,0.0508,0.0508,0.0508,0.0508,D_ins,0.0127]
                        layers = [Stucco,Concrete,Concrete,Concrete,Concrete,Insulation,Gypsum]
                    else:
                        #if it's less then 1 cm don't include in layers
                        thickness = [0.0254,0.0508,0.0508,0.0508,0.0508,0.0127]
                        layers = [Stucco,Concrete,Concrete,Concrete,Concrete,Gypsum]

                    wall = Element(0.08,0.92,thickness,layers,0.,293.,0.,"MassWall")

                    # If mass wall, assume mass floor (4" concrete)
                    # Mass (assume 4" concrete);
                    alb = 0.2
                    emis = 0.9
                    thickness = [0.054,0.054]
                    concrete = Material (1.31, 2240.0*836.8)
                    mass = Element(alb,emis,thickness,[concrete,concrete],0,293,1,"MassFloor")

                elif TypeWall[j][k] == "WoodFrame":
                    # 0.01m wood siding, tbd insulation, 1/2" gypsum
                    Rbase = 0.170284091    # based on wood siding, gypsum
                    Rins = RvalWall[j][k] - Rbase
                    D_ins = Rins * Insulation.thermalCond #depth of insulatino

                    if D_ins > 0.01:
                        thickness = [0.01,D_ins,0.0127]
                        layers = [Wood,Insulation,Gypsum]
                    else:
                        thickness = [0.01,0.0127]
                        layers = [Wood,Gypsum]

                    wall = Element(0.22,0.92,thickness,layers,0.,293.,0.,"WoodFrameWall")

                    # If wood frame wall, assume wooden floor
                    alb = 0.2
                    emis = 0.9
                    thickness = [0.05,0.05]
                    wood = Material(1.31, 2240.0*836.8)
                    mass = Element(alb,emis,thickness,[wood,wood],0.,293.,1.,"WoodFloor")

                elif TypeWall[j][k] == "SteelFrame":
                    # 1" stucco, 8" concrete, tbd insulation, 1/2" gypsum
                    Rbase = 0.271087 # based on stucco, concrete, gypsum
                    Rins = RvalWall[j][k] - Rbase
                    D_ins = Rins * Insulation.thermalCond
                    if D_ins > 0.01:
                        thickness = [0.0254,0.0508,0.0508,0.0508,0.0508,D_ins,0.0127]
                        layers = [Stucco,Concrete,Concrete,Concrete,Concrete,Insulation,Gypsum]
                    else:    # If insulation is too thin, assume no insulation
                        thickness = [0.0254,0.0508,0.0508,0.0508,0.0508,0.0127]
                        layers = [Stucco,Concrete,Concrete,Concrete,Concrete,Gypsum]
                    wall = Element(0.15,0.92,thickness,layers,0.,293.,0.,"SteelFrame")

                    # If mass wall, assume mass foor
                    # Mass (assume 4" concrete),
                    alb = 0.2
                    emis = 0.93
                    thickness = [0.05,0.05]
                    mass = Element(alb,emis,thickness,[Concrete,Concrete],0.,293.,1.,"MassFloor")

                elif TypeWall[j][k] == "MetalWall":
                    # metal siding, insulation, 1/2" gypsum
                    alb = 0.2
                    emis = 0.9
                    D_ins = max((RvalWall[j][k] * Insulation.thermalCond)/2, 0.01) #use derived insul thickness or 0.01 based on max
                    thickness = [D_ins,D_ins,0.0127]
                    materials = [Insulation,Insulation,Gypsum]
                    wall = Element(alb,emis,thickness,materials,0,293,0,"MetalWall")

                    # Mass (assume 4" concrete);
                    alb = 0.2
                    emis = 0.9
                    thickness = [0.05, 0.05]
                    concrete = Material(1.31, 2240.0*836.8)
                    mass = Element(alb,emis,thickness,[concrete,concrete],0.,293.,1.,"MassFloor")

                # Roof
                if TypeRoof[j][k] == "IEAD": #Insulation Entirely Above Deck
                    # IEAD-> membrane, insulation, decking
                     alb = 0.2
                     emis = 0.93
                     D_ins = max(RvalRoof[j][k] * Insulation.thermalCond/2.,0.01);
                     roof = Element(alb,emis,[D_ins,D_ins],[Insulation,Insulation],0.,293.,0.,"IEAD")

                elif TypeRoof[j][k] == "Attic":
                    # IEAD-> membrane, insulation, decking
                    alb = 0.2
                    emis = 0.9
                    D_ins = max(RvalRoof[j][k] * Insulation.thermalCond/2.,0.01)
                    roof = Element(alb,emis,[D_ins,D_ins],[Insulation,Insulation],0.,293.,0.,"Attic")

                elif TypeRoof[j][k] == "MetalRoof":
                    # IEAD-> membrane, insulation, decking
                    alb = 0.2
                    emis = 0.9
                    D_ins = max(RvalRoof[j][k] * Insulation.thermalCond/2.,0.01)
                    roof = Element(alb,emis,[D_ins,D_ins],[Insulation,Insulation],0.,293.,0.,"MetalRoof")

                # Define bulding energy model, set fraction of the urban floor space of this typology to zero
                refBEM[i][j][k] = BEMDef(B, mass, wall, roof, 0.0)
                refBEM[i][j][k].building.FanMax = FanFlow[j][k] # max fan flow rate (m^3/s) per DOE

                Schedule[i][j][k] = SchDef()

                Schedule[i][j][k].Elec = SchEquip   # 3x24 matrix of schedule for fraction electricity (WD,Sat,Sun)
                Schedule[i][j][k].Light = SchLight  # 3x24 matrix of schedule for fraction light (WD,Sat,Sun)
                Schedule[i][j][k].Gas = SchGas      # 3x24 matrix of schedule for fraction gas (WD,Sat,Sun)
                Schedule[i][j][k].Occ = SchOcc      # 3x24 matrix of schedule for fraction occupancy (WD,Sat,Sun)
                Schedule[i][j][k].Cool = SetCool    # 3x24 matrix of schedule for fraction cooling temp (WD,Sat,Sun)
                Schedule[i][j][k].Heat = SetHeat    # 3x24 matrix of schedule for fraction heating temp (WD,Sat,Sun)
                Schedule[i][j][k].SWH = SchSWH      # 3x24 matrix of schedule for fraction SWH (WD,Sat,Sun

                Schedule[i][j][k].Qelec = Elec[j]                   # W/m^2 (max) for electrical plug process
                Schedule[i][j][k].Qlight = Light[j]                 # W/m^2 (max) for light
                Schedule[i][j][k].Nocc = Occupant[j]/AreaFloor[j]   # Person/m^2
                Schedule[i][j][k].Qgas = Gas[j]                     # W/m^2 (max) for gas
                Schedule[i][j][k].Vent = Vent[j]/1000.0             # m^3/m^2 per person
                Schedule[i][j][k].Vswh = SHW[j]/AreaFloor[j]        # litres per hour per m^2 of floor


    # if not test serialize refDOE,refBEM,Schedule and store in resources
    if serialize_output:
        # create a binary file for serialized obj
        pickle_readDOE = open(os.path.join(DIR_UP_PATH,'resources','readDOE.pkl'), 'wb')

        # resources
        # Pickle objects, protocol 1 b/c binary file
        cPickle.dump(refDOE, pickle_readDOE,1)
        cPickle.dump(refBEM, pickle_readDOE,1)
        cPickle.dump(Schedule, pickle_readDOE,1)

        pickle_readDOE.close()

    else:
        return refDOE, refBEM, Schedule

if __name__ == "__main__":
    readDOE()


# Material ref from E+
#     1/2IN Gypsum,            !- Name
#     Smooth,                  !- Roughness
#     0.0127,                  !- Thickness {m}
#     0.1600,                  !- Conductivity {W/m-K}
#     784.9000,                !- Density {kg/m3}
#     830.0000,                !- Specific Heat {J/kg-K}
#     0.9000,                  !- Thermal Absorptance
#     0.9200,                  !- Solar Absorptance
#     0.9200;                  !- Visible Absorptance
#
# Material,
#     1IN Stucco,              !- Name
#     Smooth,                  !- Roughness
#     0.0253,                  !- Thickness
#     0.6918,                  !- Conductivity
#     1858.0000,               !- Density
#     837.0000,                !- Specific Heat
#     0.9000,                  !- Thermal Absorptance
#     0.9200,                  !- Solar Absorptance
#     0.9200;                  !- Visible Absorptance
#
# Material,
#     8IN CONCRETE HW,  !- Name
#     Rough,                   !- Roughness
#     0.2032,                  !- Thickness {m}
#     1.3110,                  !- Conductivity {W/m-K}
#     2240.0000,               !- Density {kg/m3}
#     836.8000,                !- Specific Heat {J/kg-K}
#     0.9000,                  !- Thermal Absorptance
#     0.7000,                  !- Solar Absorptance
#     0.7000;                  !- Visible Absorptance
#
# Material,
#     Mass NonRes Wall Insulation, !- Name
#     MediumRough,             !- Roughness
#     0.0484268844343858,      !- Thickness {m}
#     0.049,                   !- Conductivity {W/m-K}
#     265.0000,                !- Density {kg/m3}
#     836.8000,                !- Specific Heat {J/kg-K}
#     0.9000,                  !- Thermal Absorptance
#     0.7000,                  !- Solar Absorptance
#     0.7000;                  !- Visible Absorptance
#
# Material,
#     Std Wood 6inch,          !- Name
#     MediumSmooth,            !- Roughness
#     0.15,                    !- Thickness {m}
#     0.12,                    !- Conductivity {W/m-K}
#     540.0000,                !- Density {kg/m3}
#     1210,                    !- Specific Heat {J/kg-K}
#     0.9000000,               !- Thermal Absorptance
#     0.7000000,               !- Solar Absorptance
#     0.7000000;               !- Visible Absorptance! Common Materials
#
# Material,
#     Wood Siding,             !- Name
#     MediumSmooth,            !- Roughness
#     0.0100,                  !- Thickness {m}
#     0.1100,                  !- Conductivity {W/m-K}
#     544.6200,                !- Density {kg/m3}
#     1210.0000,               !- Specific Heat {J/kg-K}
#     0.9000,                  !- Thermal Absorptance
#     0.7800,                  !- Solar Absorptance
#     0.7800;                  !- Visible Absorptance
