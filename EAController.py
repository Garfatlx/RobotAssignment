import numpy as np
import random
import math
import copy
import pygame
from RobotClass import Robot
from const import WIDTH, HEIGHT, ROBOT_RADIUS
from Beacon import Beacon
from BeaconSensor import BeaconSensor
import Map

class NeuralNetwork:
    def __init__(self, input_size=13, hidden_size=10, output_size=2):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        # Initialize weights randomly
        self.weights_ih = np.random.randn(input_size, hidden_size) * 0.1
        self.weights_ho = np.random.randn(hidden_size, output_size) * 0.1
        self.bias_h = np.random.randn(hidden_size) * 0.1
        self.bias_o = np.random.randn(output_size) * 0.1

    def forward(self, inputs):
        # Input to hidden
        hidden = np.tanh(np.dot(inputs, self.weights_ih) + self.bias_h)
        # Hidden to output
        outputs = np.dot(hidden, self.weights_ho) + self.bias_o
        # Scale outputs to [-MAX_SPEED, MAX_SPEED]
        from const import MAX_SPEED
        return np.clip(outputs, -MAX_SPEED, MAX_SPEED)

    def set_weights(self, weights):
        # Set weights from a flattened array
        idx = 0
        # Input-to-hidden weights
        size = self.input_size * self.hidden_size
        self.weights_ih = weights[idx:idx+size].reshape(self.input_size, self.hidden_size)
        idx += size
        # Hidden-to-output weights
        size = self.hidden_size * self.output_size
        self.weights_ho = weights[idx:idx+size].reshape(self.hidden_size, self.output_size)
        idx += size
        # Hidden biases
        self.bias_h = weights[idx:idx+self.hidden_size]
        idx += self.hidden_size
        # Output biases
        self.bias_o = weights[idx:idx+self.output_size]

    def get_weights(self):
        # Return flattened weights
        return np.concatenate([
            self.weights_ih.flatten(),
            self.weights_ho.flatten(),
            self.bias_h,
            self.bias_o
        ])

class NavigatorGA:
    def __init__(self, population_size=50, mutation_rate=0.1, map_data=None, beacons=None):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.map_data = map_data
        self.beacons = beacons
        self.input_size = 13  # 12 distance sensors + 1 beacon sensor
        self.hidden_size = 10
        self.output_size = 2  # vl, vr
        self.weights_per_individual = (self.input_size * self.hidden_size +
                                      self.hidden_size * self.output_size +
                                      self.hidden_size + self.output_size)
        self.population = [np.random.randn(self.weights_per_individual) * 0.1
                          for _ in range(population_size)]
        self.ffitness = [0] * population_size

    def evaluate_individual(self, weights, steps=200):
        # Create a fresh robot for evaluation
        robot = Robot(WIDTH // 2, HEIGHT - 50, -1.2, ROBOT_RADIUS, self.map_data)
        beacon_sensor = BeaconSensor(robot, relative_angle=0, fov=math.radians(360), range=200, precision=0)
        robot.add_sensor(beacon_sensor)
        nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        nn.set_weights(weights)

        collisions = 0
        fitness = 0
        for _ in range(steps):
            # Get sensor readings
            sensor_readings = [sensor.get_distance(self.map_data) for sensor in robot.sensors[:-1]]
            beacon_reading = beacon_sensor.get_observed_pose(self.beacons)
            beacon_dist = beacon_reading[0] if beacon_reading else 200  # Default to max range
            inputs = np.array(sensor_readings + [beacon_dist]) / 200  # Normalize to [0, 1]
            # Get NN outputs
            vl, vr = nn.forward(inputs)
            robot.vl, robot.vr = vl, vr
            # Move robot
            robot.move(vl, vr)
            # Update Kalman filter
            robot.kalman_filter(beacon_sensor.get_observed_pose(self.beacons))
            # Check collisions
            if robot.get_collision():
                collisions += 1
            fitness += (robot.vl + robot.vr)*(1-(np.abs(robot.vl - robot.vr))**2)
        # # Fitness: minimize distance to first beacon, penalize collisions
        # x, y, _ = robot.get_pos()
        # beacon_x, beacon_y = self.beacons[0].x, self.beacons[0].y
        # distance_to_beacon = math.sqrt((x - beacon_x)**2 + (y - beacon_y)**2)
        # fitness = -distance_to_beacon - 100 * collisions
        finalmapscore = np.sum(np.abs(robot.get_mapped_grid()))/20000
        fitness = fitness/steps - collisions
        robot.destroy()
        return fitness
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def weighted_bce(self, labels, logits, w_1=2.0, w_0=1.0):
        probs = self.sigmoid(logits)
        eps = 1e-9  # for numerical stability
        return -np.mean(
            w_1 * labels * np.log(probs + eps) +
            w_0 * (1 - labels) * np.log(1 - probs + eps)
        )
    def select_parent(self):
        # Tournament selection
        tournament_size = 5
        tournament = random.sample(list(zip(self.fitness, self.population)), tournament_size)
        return max(tournament, key=lambda x: x[0])[1]

    def crossover(self, parent1, parent2):
        # Blend crossover
        alpha = random.random()
        child = alpha * parent1 + (1 - alpha) * parent2
        return child

    def mutate(self, individual):
        # Add Gaussian noise
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                individual[i] += np.random.randn() * 0.1
        return individual

    def evolve(self, generations=10, steps=200):
        for gen in range(generations):
            # Evaluate population
            self.fitness = [self.evaluate_individual(weights, steps) for weights in self.population]
            # Create new population
            new_population = []
            # Elitism: keep best individual
            best_idx = np.argmax(self.fitness)
            new_population.append(self.population[best_idx])
            # Generate rest of population
            while len(new_population) < self.population_size:
                parent1 = self.select_parent()
                parent2 = self.select_parent()
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population
            # Print progress
            print(f"Generation {gen+1}: Best Fitness = {max(self.fitness)}")
        # Return best NN
        best_idx = np.argmax(self.fitness)
        best_weights = self.population[best_idx]
        nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        nn.set_weights(best_weights)
        return nn

    def get_best_controller(self):
        best_idx = np.argmax(self.fitness)
        best_weights = self.population[best_idx]
        nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        nn.set_weights(best_weights)
        return nn