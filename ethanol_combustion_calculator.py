import math
from sympy import symbols, solve

selection = input("Select:\n1 - Volume\n2 - Pipe Dimensions\n")

V = None
if selection == "2":
    R = float(input("Inner Diameter in mm: "))
    L = float(input("Length in mm: "))
elif selection == "1":
    V = float(input("Volume in Liters: "))

h = float(input("Altitude in m: "))
T = float(input("Temperature in C: "))

class environment:
    temperature = T + 273.15 #K
    altitude = h #m
    h_reference = 0 #m
    p0 = 101325 #Pa
    g = 9.80665 #m/s^2
    M = 0.0289644 #kg/mol
    R = 8.31432 #J/(mol*K)
    pressure = p0 * math.exp(-1 * g * M * (altitude - h_reference) / (R * temperature)) #Pa

class chamber:
    if V == None:
        half_diameter = R / 2  # mm
        length = L  # mm
        V = math.pi * half_diameter ** 2 * length * 10 ** -6  # L
    volume = V

class o2:
    pressure = environment.pressure * 0.2095 #Pa
    volume = chamber.volume / 1000 #m^3
    a = 1.382 #constant
    b = 0.03186 #constant

class ethanol:
    pressure = environment.pressure * 0.11075 #Pa
    volume = chamber.volume / 1000 # %11.075 is middle of the flammable limits | m^3
    molar_mass = 0.04607 #kg/mol
    combustion_enthalpy = 1366.8 #kJ/mol at 25 C
    a = 12.18 #constant
    b = 0.08407 #constant

class DIPPR105:
    A = 99.3974
    B = 0.310729
    C = 513.18
    D = 0.305143

n_o2 = symbols("n_o2")
expr = (o2.pressure + o2.a * (n_o2 / o2.volume)**2) * (o2.volume / n_o2 - o2.b) - environment.R * environment.temperature
solution_n_o2 = solve(expr)
o2_number_of_moles = solution_n_o2[0]

n_ethanol = symbols("n_ethanol")
expr = (ethanol.pressure + ethanol.a * (n_ethanol / ethanol.volume)**2) * (ethanol.volume / n_ethanol - ethanol.b) - environment.R * environment.temperature
solution_n_ethanol = solve(expr)
ethanol_number_of_moles = solution_n_ethanol[0]

ethanol_density = DIPPR105.A / (DIPPR105.B ** (1 + (1 - environment.temperature / DIPPR105.C) ** DIPPR105.D)) / 1000 #kg/L
ethanol_mass = ethanol.molar_mass * ethanol_number_of_moles #kg
ethanol_volume = ethanol_mass / ethanol_density #L

used_ethanol = o2_number_of_moles / 3 #mol
combustion_energy = used_ethanol * ethanol.combustion_enthalpy #kJ (approx)

print("Atmospheric Pressure = " + str(round(environment.pressure, 2)) + " Pa")
print("Chamber Volume = " + str(round(chamber.volume * 1000, 2)) + " mL")
print("Optimum Amount of Ethanol = " + str(round(ethanol_number_of_moles, 6)) + " mol")
print("Optimum Mass of Ethanol = " + str(round(ethanol_mass * 1000, 3)) + " g")
print("Liquid Volume of Ethanol = " + str(round(ethanol_volume * 1000, 3)) + " mL")
print("Reaction Efficiency = " + str(round(used_ethanol / ethanol_number_of_moles * 100, 2)) + "%")
print("Approximate Combustion Energy = " + str(round(combustion_energy, 2)) + " kJ")

input("\nPress enter to exit...")
