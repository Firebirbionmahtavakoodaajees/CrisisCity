"""Crisis City"""

'''Imports'''
import random
import time
import numpy as np

'''Variables'''
#Starting stats
event_chance = 6
year = 0
population = 50000

#Starting general stats
money = 1000000
happiness = 50
health = 50
energy = 50

#Starting population change stats
base_birth_rate = 0.005
base_death_rate = 0.012

#Q-Learning
learning_rate = 0.1
discount_factor = 0.95
exploration_rate = 0.3
exploration_decay = 0.995

# Discretize states
money_bins = 5
happiness_bins = 5
health_bins = 5
energy_bins = 5
population_bins = 5

# Track previous state and score for delta calculation
previous_score = 300
previous_state = None
previous_action = None

'''Functions'''
def clamp(value, min_val=0, max_val=100):
    return max(min_val, min(value, max_val))

def score():
    """A simplified, balanced score."""
    normalized_money = min(money / 10000, 100) if money > 0 else 0
    normalized_population = min(population / 500, 100)

    return (normalized_money * 0.2 +
            happiness * 0.3 +
            health * 0.25 +
            energy * 0.15 +
            normalized_population * 0.1)

#events
def flood():
    global money, happiness, health, energy, deaths, birth_rate
    print("A flood hits the area!")
    money -= random.randint(5, 20)
    happiness -= random.randint(5, 15)
    health -= random.randint(5, 10)
    energy -= random.randint(5, 10)
    if 'deaths' in globals():
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
    global health, happiness, energy, deaths, population
    print("A disease spreads!")
    health_impact = random.randint(5, 15) * (population / 50000)
    health -= int(health_impact)
    happiness -= random.randint(5, 10)
    energy -= random.randint(5, 15)
    additional_deaths = int(population * random.uniform(0.001, 0.005))
    deaths += additional_deaths

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
    population = int(population * 1.02)
    birth_rate += 0.002

events = [flood, power_outage, disease, protest, economic_boom]

#AI Actions
def build_hospital():
    global money, health, happiness, population
    print("AI builds a hospital.")
    cost = 1500
    if money >= cost:
        money -= cost
        # Health benefit depends on current health (diminishing returns)
        health_gain = max(5, int((100 - health) * 0.15))
        health += health_gain
        happiness += 5
        print(f"Cost: ${cost}, Health improved by {health_gain}.")
    else:
        print(f"Not enough money! Need ${cost}, have ${money}")
        do_nothing()

def invest_energy():
    global money, energy, happiness
    print("AI invests in green energy.")
    cost = 800
    if money >= cost:
        money -= cost
        energy += 25
        happiness += 3
        print(f"Cost: ${cost}, Energy improved by 25.")
    else:
        print(f"Not enough money! Need ${cost}, have ${money}")
        do_nothing()

def raise_taxes():
    global money, happiness, health, energy
    print("AI raises taxes.")
    tax_income = population * 0.02
    money += int(tax_income)
    happiness -= 15
    health -= 2
    energy -= 2
    print(f"Tax revenue: ${int(tax_income)}, Happiness decreased by 15.")

def do_nothing():
    print("AI does nothing.")
    global happiness, health, energy
    happiness += 1
    health += 1
    energy += 1

# AI Action space
actions = [build_hospital, invest_energy, raise_taxes, do_nothing]
num_actions = len(actions)

# Initialize Q-table with small random values
state_space_size = money_bins * happiness_bins * health_bins * energy_bins * population_bins
q_table = np.random.uniform(-0.1, 0.1, (state_space_size, num_actions))

#system functions
def apply_clamp():
    global happiness, health, energy, money
    happiness = clamp(happiness)
    health = clamp(health)
    energy = clamp(energy)
    money = max(0, money)

def show_stats():
    print(f"Year: {year}")
    print(f"Money: ${money}")
    print(f"Happiness: {happiness}")
    print(f"Health: {health}")
    print(f"Energy: {energy}")
    print(f"Population: {population}")
    if 'birth_rate' in globals():
        print(f"Birth rate: {birth_rate:.4f}")
    if 'effective_death_rate' in globals():
        print(f"Death rate: {effective_death_rate:.4f}")
    print("-" * 20)

def discretize_state():
    """Convert continuous state to discrete state index - FIXED TYPE ISSUE"""
    # Convert money to normalized value (0-100 scale)
    money_normalized = money / 10000.0
    money_normalized = max(0.0, min(100.0, money_normalized))

    # Convert to index
    money_idx = int(money_normalized / (100.0 / money_bins))
    money_idx = min(money_bins - 1, max(0, money_idx))

    # Other indices
    happiness_idx = int(happiness / (100.0 / happiness_bins))
    happiness_idx = min(happiness_bins - 1, max(0, happiness_idx))

    health_idx = int(health / (100.0 / health_bins))
    health_idx = min(health_bins - 1, max(0, health_idx))

    energy_idx = int(energy / (100.0 / energy_bins))
    energy_idx = min(energy_bins - 1, max(0, energy_idx))

    # Population discretization
    pop_ratio = population / 50000.0
    pop_level = min(2.0, max(0.0, pop_ratio))
    population_idx = int(pop_level * population_bins / 2.0)
    population_idx = min(population_bins - 1, max(0, population_idx))

    # Calculate unique state index
    state_idx = ((((money_idx * happiness_bins + happiness_idx) * health_bins + health_idx) *
                  energy_bins + energy_idx) * population_bins + population_idx)

    return int(state_idx)

def choose_action(state_idx):
    """Choose action using epsilon-greedy policy"""
    global exploration_rate

    if random.random() < exploration_rate:
        return random.randint(0, num_actions - 1)
    else:
        state_idx = min(state_idx, q_table.shape[0] - 1)
        return int(np.argmax(q_table[state_idx]))

def update_q_table(prev_state, prev_action, reward, new_state):
    """Update Q-table using Q-learning algorithm"""
    global q_table, exploration_rate

    prev_state = min(int(prev_state), q_table.shape[0] - 1)
    new_state = min(int(new_state), q_table.shape[0] - 1)

    best_future_q = np.max(q_table[new_state])
    current_q = q_table[prev_state, prev_action]

    q_table[prev_state, prev_action] = current_q + learning_rate * (
        reward + discount_factor * best_future_q - current_q
    )

    exploration_rate *= exploration_decay
    exploration_rate = max(0.05, exploration_rate)

def ai_take_action():
    """Main AI decision function"""
    global previous_state, previous_action, previous_score

    current_state = discretize_state()
    action_idx = choose_action(current_state)

    previous_state = current_state
    previous_action = action_idx
    previous_score = score()

    actions[action_idx]()

    return action_idx

'''Main loop'''
print("Crisis City Simulation Starting...\n")
time.sleep(3)

while True:
    time.sleep(1)
    year += 1
    print(f"\n{'='*50}")
    print(f"YEAR {year}")
    print(f"{'='*50}")

    # Population dynamics
    effective_death_rate = base_death_rate * (1.0 - (health / 200.0))
    effective_death_rate = max(0.001, effective_death_rate)

    birth_rate = base_birth_rate * (0.8 + (happiness / 125.0))
    birth_rate = max(0.005, birth_rate)

    births = int(population * birth_rate)
    deaths = int(population * effective_death_rate)

    population += births - deaths
    population = max(100, population)

    # Economic system
    tax_efficiency = (happiness / 100.0) * (health / 100.0)
    money += int(population * 0.01 * tax_efficiency)

    # Maintenance costs - REDUCED
    base_maintenance = population * 0.005
    energy_maintenance = max(0, (energy - 50) * 5)
    health_maintenance = max(0, (health - 50) * 3)
    money -= int(base_maintenance + energy_maintenance + health_maintenance)

    # Natural decay - FIXED: Use percentages, not raw numbers
    health_decay_percent = 0.01  # 1% decay per year
    health -= health * health_decay_percent

    energy_decay_percent = 0.005  # 0.5% decay per year
    energy -= energy * energy_decay_percent

    # Happiness adjustment
    if money > 0:
        happiness += 1
    else:
        happiness -= 3

    # Random events
    if random.randint(1, 100) <= event_chance:
        event = random.choice(events)
        event()
    else:
        print("No events happen this year.")

    # AI Decision
    print("\n--- AI Decision ---")
    action_idx = ai_take_action()
    action_names = ["Build Hospital", "Invest in Energy", "Raise Taxes", "Do Nothing"]
    print(f"AI chose: {action_names[action_idx]}")

    # Calculate reward and update Q-table
    current_score = score()
    reward = current_score - previous_score

    if previous_state is not None and previous_action is not None:
        new_state = discretize_state()
        update_q_table(previous_state, previous_action, reward, new_state)
        print(f"Reward: {reward:.2f}")
        print(f"Exploration rate: {exploration_rate:.3f}")

    print(f"Overall Score: {current_score:.1f}")

    # Apply limits
    apply_clamp()

    # Display stats
    show_stats()

    # Game over conditions
    if population <= 0:
        print("\n" + "!"*50)
        print("GAME OVER: The city has collapsed. Population is zero.")
        print("!"*50)
        break

    if happiness <= 0:
        print("\n" + "!"*50)
        print("GAME OVER: The city has collapsed due to unrest.")
        print("!"*50)
        break