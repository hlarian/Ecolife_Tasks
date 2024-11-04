import numpy as np
import random
import utils

class Firefly:
    def __init__(self, params, server_pair, function_name, ci_avg):
        self.params = params                # Firefly algorithm parameters (population size, alpha, beta, etc.)
        self.server_pair = server_pair      # Pair of servers (old and new)
        self.function_name = function_name  # The function being optimized
        self.ci_avg = ci_avg                # Average carbon intensity

        # Initialize fireflies
        self.population = self.initialize_population()
        self.brightness = np.zeros(self.params['population_size'])  # Stores brightness (fitness) of each firefly
        self.prev_ci = None               # Initialize previous carbon intensity for adaptation
        self.prev_fn = None               # Initialize previous invocation length

    def initialize_population(self):
        """Initialize population with random scheduling configurations."""
        population = []
        for _ in range(self.params['population_size']):
            firefly = [random.choice([0, 1]), random.choice(self.params['kat_times'])]
            population.append(firefly)
        return np.array(population, dtype=float)

    def fitness(self, firefly_position, ci, past_interval):
        """Calculates fitness based on carbon footprint and service time, adapting to current conditions."""
        ka_loc, kat = firefly_position
        old_kat_carbon = utils.compute_kat(self.function_name, self.server_pair[0], kat, ci)
        new_kat_carbon = utils.compute_kat(self.function_name, self.server_pair[1], kat, ci)
        cold_carbon, warm_carbon = utils.compute_exe(self.function_name, self.server_pair, ci)

        # Calculate performance scores
        old_st = utils.get_st(self.function_name, self.server_pair[0])
        new_st = utils.get_st(self.function_name, self.server_pair[1])

        # Calculate probabilities for cold and warm start
        cold_prob, warm_prob = self.prob_cold(past_interval, kat)
        expected_service_time = cold_prob * ((1 - ka_loc) * old_st[0] + ka_loc * new_st[0]) + warm_prob * ((1 - ka_loc) * old_st[1] + ka_loc * new_st[1])
        expected_carbon_cost = cold_prob * ((1 - ka_loc) * cold_carbon[0] + ka_loc * cold_carbon[1]) + warm_prob * ((1 - ka_loc) * warm_carbon[0] + ka_loc * warm_carbon[1])

        return self.params['lambda'] * expected_service_time + (1 - self.params['lambda']) * expected_carbon_cost

    def prob_cold(self, cur_interval, kat):
        """Calculate cold start probability based on invocation intervals."""
        if len(cur_interval) == 0:
            return 0.5, 0.5
        cold = sum(1 for interval in cur_interval if interval > kat)
        warm = len(cur_interval) - cold
        return cold / len(cur_interval), warm / len(cur_interval)

    def move_firefly(self, i, j):
        """Move firefly i towards firefly j if j is brighter."""
        distance = np.linalg.norm(self.population[i] - self.population[j])
        attractiveness = self.params['beta'] * np.exp(-self.params['gamma'] * distance ** 2)
        self.population[i] += attractiveness * (self.population[j] - self.population[i])
        self.population[i] += self.params['alpha'] * (random.random() - 0.5)

    def main(self, ci, past_interval):
        """Main optimization loop for the Firefly Algorithm with dynamic environmental adaptation."""
        
        # Calculate brightness for each firefly based on current ci and past_interval
        for i in range(self.params['population_size']):
            self.brightness[i] = self.fitness(self.population[i], ci, past_interval)
        
        # Update fireflies based on brightness comparison
        for i in range(self.params['population_size']):
            for j in range(self.params['population_size']):
                if self.brightness[j] > self.brightness[i]:
                    self.move_firefly(i, j)
                    
        # Determine the best solution after one update
        best_index = np.argmax(self.brightness)
        best_solution = self.population[best_index]

        # Update previous values for future adaptation
        self.prev_ci = ci
        self.prev_fn = len(past_interval)
        
        return best_solution
