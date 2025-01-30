import random
import itertools
from math import comb


class Dice:
    def __init__(self, description: str):
        parts = description.split('d')
        if len(parts) != 2:
            raise ValueError("Invalid dice description format.")
        self.times = int(parts[0])
        self.num_faces = int(parts[1])
        if self.times <= 0 or self.num_faces <= 0:
            raise ValueError("Dice times and faces must be positive integers.")
    
    def roll(self):
        try:
            results = []
            for _ in range(self.times):
                result = random.randint(1, self.num_faces)
                results.append(result)
            return results if self.times > 1 else results[0]
        except Exception as e:
            print(f"An error occurred during the roll: {e}")
            return [0]  # Return a list with one zero element to indicate an error
        
    def calculate_probability(self, target_value):
        # Total number of outcomes
        total_outcomes = self.num_faces ** self.times
        
        # Number of favorable outcomes
        favorable_outcomes = 0
        
        for r in range(1, self.times + 1):
            for combo in itertools.product(range(1, self.num_faces + 1), repeat=r):
                if sum(combo) == target_value:
                    favorable_outcomes += comb(self.times, r)
        
        # Calculate probability
        probability = (favorable_outcomes / total_outcomes) * 100
        return probability
    
    def dice_probability_table(self, target_value):
        table = {}
        for i in range(1, self.num_faces + 1):
            for j in range(1, self.num_faces + 1):
                table[i, j] = (i + j) / 2
        return table

