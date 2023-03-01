selection = int(input("""
----------FUELS----------
1 - Ethanol
2 - Diethyl Ether
3 - HHO

Selection: """))

for i in range(1,4):
    if selection == i:
        if i == 1:
            file = "ethanol_rifle_calculator"
        elif i == 2:
            file = "diethyl_ether_rifle_calculator"
        elif i == 3:
            file = "HHO_rifle_calculator"

fuel = f"\nFuel: {file}".replace("_rifle_calculator", "").replace("_", " ")

print(fuel.upper())

exec(open(f"{file}.py").read())
