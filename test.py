BUS_SPACE = 100

def bus_free_space(passengers: int): 
    global BUS_SPACE
    if passengers < 0: 
        return f"Passengers amount has to be greater or equalt to 0"
    if passengers > BUS_SPACE-1:
        return "Bus does not have enough space"

    BUS_SPACE -= passengers

    if BUS_SPACE-1 == 0:
        return "Bus is full now"
    return f"Bus space remaining: {BUS_SPACE-1}"

while True:
    value = input("Enter passengers amount: ")
    print(bus_free_space(int(value)))
