"""Crisis City"""

'''Imports'''
import random
import time

'''Variables'''
#Starting stats

#Event Chance in percentage
event_chance = 30

#Starting time
year = 0
population = 1000

#Starting general stats
money = 50
happiness = 50
health = 50
energy = 50
# trust = 10

#Starting population change stats
birth_rate = 0.010
death_rate = 0.010

'''Functions'''
def clamp(value, min_val=0, max_val=100):
    return max(min_val, min(value, max_val))

def score():
    return money + happiness + health + energy + (population // 10)

#events
def flood():
    global money, happiness, health, energy, deaths, birth_rate
    print("A flood hits the area!")
    money -= random.randint(5, 20)
    happiness -= random.randint(5, 15)
    health -= random.randint(5, 10)
    energy -= random.randint(5, 10)
    deaths = int(deaths * 1.2)
    birth_rate -= 0.0005

def power_outage():
    global happiness, energy, population, birth_rate
    print("A power outage occurs!")
    happiness -= random.randint(3, 10)
    energy -= random.randint(5, 15)
    population = int(population * 0.99)
    birth_rate -= 0.0005

def disease():
    global health, happiness, energy, deaths
    print("A disease spreads!")
    health -= random.randint(10, 25)
    happiness -= random.randint(5, 10)
    energy -= random.randint(5, 15)
    deaths = int(deaths * 1.2)

def protest():
    global happiness, money, population, birth_rate
    print("Protests break out!")
    happiness -= random.randint(5, 15)
    money -= random.randint(0, 10)
    population = int(population * 0.97)
    birth_rate -= 0.001

def economic_boom():
    global money, happiness, population, birth_rate
    print("An economic boom boosts the economy!")
    money += random.randint(10, 25)
    happiness += random.randint(5, 15)
    population = int(population * 1.2)
    birth_rate += 0.002

events = [flood, power_outage, disease, protest, economic_boom]

#AI Actions

def build_hospital():
    global money, health, happiness
    print("AI builds a hospital.")
    money -= 10
    health += 20
    happiness += 5

def invest_energy():
    global money, energy
    print("AI invests in green energy.")
    money -= 10
    energy += 15

def raise_taxes():
    global money, happiness
    print("AI raises taxes.")
    money += 15
    happiness -= 10

def do_nothing():
    print("AI does nothing.")
    pass


#system functions
def apply_clamp():
    global money, happiness, health, energy, population
    money = clamp(money)
    happiness = clamp(happiness)
    health = clamp(health)
    energy = clamp(energy)

def show_stats():
    print(f"Money: {money}")
    print(f"Happiness: {happiness}")
    print(f"Health: {health}")
    print(f"Energy: {energy}")
    print(f"Population: {population}")
    print(f"Birth rate: {birth_rate}")
    print(f"Death rate: {effective_death_rate}")
    print("-" * 20)


actions = [build_hospital, invest_energy, raise_taxes, do_nothing]

Q = {}          # Q-table
alpha = 0.1     # learning rate
gamma = 0.9     # discount factor
epsilon = 0.1   # exploration rate

def choose_action(state):
    if random.random() < epsilon:
        return random.choice(actions)
    q_values = [Q.get((tuple(state), a.__name__), 0) for a in actions]
    max_q = max(q_values)
    return actions[q_values.index(max_q)]

def update_q(state, action, reward, next_state):
    old_value = Q.get((tuple(state), action.__name__), 0)
    future_reward = max([Q.get((tuple(next_state), a.__name__), 0) for a in actions])
    new_value = old_value + alpha * (reward + gamma * future_reward - old_value)
    Q[(tuple(state), action.__name__)] = new_value


'''Hype up text'''
print("Get ready... The simulation is starting :)")

'''Main loop'''
while True:
    #Time flies
    time.sleep(5)
    year += 1
    print(f"\n===== YEAR {year} =====")

    #Population growth and shrinkage
    effective_death_rate = death_rate * (1 + (1 - health / 100))

    births = int(population * birth_rate)
    deaths = int(population * effective_death_rate)

    population += births
    population -= deaths
    population = int(population)

    # Taxes without taxes
    money += population * 0.02  # taxes
    money -= population * 0.015  # maintenance

    # Health & energy pressure IDK SHOULD WE ADD THIS
    health -= population * 0.0002
    energy -= population * 0.0003

    # Happiness depends on stability
    if money > 0:
        happiness += 0.2
    else:
        happiness -= 0.7

    #AI
    event = random.choice(events)

    event_happens = random.randint(1, 100)
    if event_happens <= event_chance:
        event()
    else:
        print("No events happen")

    print("Score:", score())

    # More AI
    state = [population, money, health, happiness, energy]  # current state
    action = choose_action(state)                            # choose action
    action()                                                 # perform the action
    next_state = [population, money, health, happiness, energy]  # state after action
    reward = score()                                         # reward for AI
    update_q(state, action, reward, next_state)             # update Q-table


    #Clamp (check maximum and minimum values)
    apply_clamp()
    population = max(int(population), 0)

    # --- Display ---
    show_stats()

    # --- Game over conditions ---
    if population <= 0:
        print("The city has collapsed. Population is zero.")
        break

    if happiness <= 0:
        print("The city has collapsed due to unrest.")
        break
