import math
from sympy import symbols, solve


class environment:
    temperature = float(input("Temperature in C: ")) + 273.15  # K
    altitude = float(input("Altitude in m: "))  # m
    h_reference = 0  # m
    p0 = 101325  # Pa
    g = 9.80665  # m/s²
    M = 0.0289644  # kg/mol
    R = 8.31432  # J/(mol*K)
    pressure = p0 * math.exp(-1 * g * M * (altitude - h_reference) / (R * temperature))  # Pa
    air_density = pressure / ((R/M)*temperature)  # kg/m³


class chamber:
    volume = float(input("Chamber Volume in Liters: "))
    pressure = None
    temperature = None
    # specific_heat_capacity = 0.89 #J/g °C | Aluminum


class o2:
    pressure = environment.pressure * 0.2095  # Pa
    volume = chamber.volume / 1000  # m³
    a = 1.382  # constant
    b = 0.03186  # constant


class diethyl_ether:
    LEL = 1.9  # %  | Room temperature and atmospheric pressure using a 2 inch tube with spark ignition
    UEL = 36  # %
    pressure = environment.pressure * ((LEL + UEL) / 2) / 100  # Pa  | Required partial pressure to acquire the middle of the flammable limits (considered the most explosive ratio)
    volume = chamber.volume / 1000  # m³
    molar_mass = 0.04607  # kg/mol
    # gross_calorific_value = 1364.47 #kJ/mol at 25 C°
    # net_calorific_value = 1230.6 #kJ/mol at 25 C°
    a = 17.61 # constant
    b = 0.1344 # constant


class DIPPR105:
    A = 70.6361
    B = 0.26782
    C = 466.578
    D = 0.28243


n_o2 = symbols("n_o2")
expr = (o2.pressure + o2.a * (n_o2 / o2.volume)**2) * (o2.volume / n_o2 - o2.b) - environment.R * environment.temperature
solution_n_o2 = solve(expr)
o2_number_of_moles = solution_n_o2[0]

n_diethyl_ether = symbols("n_diethyl_ether")
expr = (diethyl_ether.pressure + diethyl_ether.a * (n_diethyl_ether / diethyl_ether.volume)**2) * (diethyl_ether.volume / n_diethyl_ether - diethyl_ether.b) - environment.R * environment.temperature
solution_n_diethyl_ether = solve(expr)
diethyl_ether_number_of_moles = solution_n_diethyl_ether[0]

diethyl_ether_density = DIPPR105.A / (DIPPR105.B ** (1 + (1 - environment.temperature / DIPPR105.C) ** DIPPR105.D)) / 1000  # kg/L
diethyl_ether_mass = diethyl_ether.molar_mass * diethyl_ether_number_of_moles  # kg
diethyl_ether_volume = diethyl_ether_mass / diethyl_ether_density  # L

used_diethyl_ether = o2_number_of_moles / 6  # mol
reaction_efficiency = used_diethyl_ether / diethyl_ether_number_of_moles


class number_of_moles:
    # Note: C4H10O + 6O2 -------> 4CO2 + 5H2O
    products = used_diethyl_ether * 9
    leftover_diethyl_ether = diethyl_ether_number_of_moles - used_diethyl_ether
    atmospheric_gases = o2_number_of_moles * (environment.pressure / o2.pressure)
    all_gases_after_reaction = products + leftover_diethyl_ether + atmospheric_gases
    co2 = products * 4/9
    h2o = products * 5/9


class enthalpy_of_formation:
    diethyl_ether = -252.7  # kJ/mol
    co2 = -393.5  # kJ/mol
    h2o = -241.8  # kJ/mol


combustion_energy = (enthalpy_of_formation.diethyl_ether * used_diethyl_ether) - (enthalpy_of_formation.co2 * number_of_moles.co2) - (enthalpy_of_formation.h2o * number_of_moles.h2o) #kJ
chamber.pressure = combustion_energy / chamber.volume  # kJ/Liter = MPa
net_pressure = chamber.pressure - environment.pressure/10**6


class barrel:
    radius = float(input("Barrel Inner Diameter in mm: "))/2
    length = float(input("Barrel Length in mm: "))
    area = math.pi * radius ** 2  # mm²
    volume = area * length / 10**6  # L
    total_volume = chamber.volume + volume  # L
    muzzle_pressure = (chamber.pressure / (total_volume/chamber.volume)) - (environment.pressure/10**6)  # MPa
    mass_of_air = environment.air_density * (volume / 1000)  # kg


class projectile:
    mass = float(input("Projectile Mass in grams: "))


class forces:
    initial_force = barrel.area * net_pressure
    muzzle_force = barrel.area * barrel.muzzle_pressure
    avreage_force = (initial_force + muzzle_force) / 2
    COF = 0.5192971331  # measured coefficient | 0.1mm Printed PLA - Extruded Aluminum Pipe
    friction_force = (projectile.mass/1000)*environment.g * COF  # N
    net_force = avreage_force - friction_force


class motion:
    acceleration = forces.net_force / ((projectile.mass / 1000) + barrel.mass_of_air) # m/s²
    muzzle_velocity = math.sqrt(2 * acceleration * (barrel.length / 1000))  # m/s
    kinetic_energy = (1 / 2) * (projectile.mass / 1000) * muzzle_velocity ** 2  # J
    time_in_barrel = (muzzle_velocity / acceleration) # s
    rifle_efficiency = kinetic_energy / (combustion_energy * 1000) * 100  # %


print("\n-----------CHAMBER-----------")
print(f"Atmospheric Pressure = {round(environment.pressure, 2)} Pa")
print(f"Chamber Volume = {round(chamber.volume * 10**3, 2)} mL")
print(f"Optimum Amount of Diethyl Ether = {round(diethyl_ether_number_of_moles, 6)} mol")
print(f"Optimum Mass of Diethyl Ether = {round(diethyl_ether_mass * 10**3, 3)} g")
print(f"Liquid Volume of Diethyl Ether = {round(diethyl_ether_volume * 10**3, 3)} mL")
print(f"Reaction Efficiency = {round(reaction_efficiency * 100, 2)}%")
print(f"Combustion Energy = {round(combustion_energy, 2)} kJ")
print(f"Chamber Pressure = {round(chamber.pressure, 3)} MPa")
print(f"Net Pressure = {round(net_pressure, 3)} MPa")

print("\n----------PROJECTILE----------")
print(f"Force on Projectile @Chamber = {round(forces.initial_force, 2)} Newtons")
print(f"Force on Projectile @Muzzle = {round(forces.muzzle_force, 2)} Newtons")
print(f"Average Barrel Force = {round(forces.avreage_force, 2)} Newtons")
print(f"Friction Force = {round(forces.friction_force, 4)} Newtons")
print(f"Net Force on Projectile = {round(forces.net_force, 2)} Newtons")
print(f"Acceleration = {round(motion.acceleration/1000, 2)} km/s²   |   {round(motion.acceleration/9.81, 2)} g")
print(f"Muzzle Velocity = {round(motion.muzzle_velocity, 2)} m/s    |   Mach {round(motion.muzzle_velocity / 343, 2)}")
print(f"Kinetic Energy = {round(motion.kinetic_energy, 2)} Joules")
print(f"Time in Barrel = {round(motion.time_in_barrel * 1000, 2)} ms")
print(f"Rifle Efficiency = {round(motion.rifle_efficiency, 2)}%")

input("\nPress enter to exit...")
