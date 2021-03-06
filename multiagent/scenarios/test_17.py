import numpy as np
import itertools
from multiagent.core import World, Agent, Landmark
from multiagent.scenario import BaseScenario


class Scenario(BaseScenario):
    def make_world(self):
        world = World()
        # set any world properties first
        world.dim_c = 2
        num_agents = 2
        num_landmarks = 2
        num_obstacles = 0
        # generate one-hot encoding for unique hidden goals
        one_hot_array = list(itertools.product([0, 1], repeat=num_landmarks))
        # generate colours for goal identification
        colours = []
        for _ in range(num_landmarks):
            colours.append(np.random.uniform(-1, +1, 3))
        # add agents
        world.agents = [Agent() for i in range(num_agents)]
        for i, agent in enumerate(world.agents):
            agent.name = 'agent %d' % i
            agent.collide = True
            agent.silent = True
            agent.size = 0.08
            agent.color = colours[i]
        # add landmarks
        world.landmarks = [Landmark() for i in range(num_landmarks)]
        for i, landmark in enumerate(world.landmarks):
            landmark.name = 'landmark %d' % i
            landmark.collide = False
            landmark.movable = False
            landmark.color = colours[i]
            landmark.id = one_hot_array[i + 1]
        # add obstacles
        world.obstacles = [Landmark() for i in range(num_obstacles)]
        for i, obstacle in enumerate(world.obstacles):
            obstacle.name = 'obstacle %d' % i
            obstacle.collide = True
            obstacle.movable = False
            obstacle.size = 0.30
            obstacle.boundary = False
            obstacle.color = np.array([0.25, 0.25, 0.25])
        # make initial conditions
        self.reset_world(world)
        return world

    def assign_goals(self, i, agent):
        # assign each agent to a unique set of goals in one-hot encoding
        if i == 0:
            agent.hidden_goals = (0, 1)
        elif i == 1:
            agent.hidden_goals = (1, 0)

    def create_wall(self, world):
        # create a wall of obstacles
        pass

    def reset_world(self, world):
        # properties for agents
        for i, agent in enumerate(world.agents):
            pass
        # properties for landmarks
        for i, agent in enumerate(world.agents):
            pass
        # properties for obstacles
        for i, obstacle in enumerate(world.obstacles):
            pass
        # set initial states
        for i, agent in enumerate(world.agents):
            agent.state.p_pos = np.random.uniform(-1, +1, world.dim_p)
            agent.state.p_vel = np.zeros(world.dim_p)
            agent.state.c = np.zeros(world.dim_c)
            self.assign_goals(i, agent)
        for i, landmark in enumerate(world.landmarks):
            landmark.state.p_pos = np.random.uniform(-1, +1, world.dim_p)
            landmark.state.p_vel = np.zeros(world.dim_p)
        for i, obstacle in enumerate(world.obstacles):
            pass
        self.create_wall(world)

    def benchmark_data(self, agent, world):
        rew = 0
        collisions = 0
        occupied_landmarks = 0
        min_dists = 0
        for l in world.landmarks:
            dists = [np.sqrt(np.sum(np.square(a.state.p_pos - l.state.p_pos))) for a in world.agents]
            min_dists += min(dists)
            rew -= min(dists)
            if min(dists) < 0.1:
                occupied_landmarks += 1
        if agent.collide:
            for a in world.agents:
                if self.is_collision(a, agent):
                    rew -= 1
                    collisions += 1
        return (rew, collisions, min_dists, occupied_landmarks)

    def is_collision(self, agent1, agent2):
        delta_pos = agent1.state.p_pos - agent2.state.p_pos
        dist = np.sqrt(np.sum(np.square(delta_pos)))
        dist_min = agent1.size + agent2.size
        return True if dist < dist_min else False

    def reward(self, agent, world):
        # Agents are rewarded based on minimum agent distance to each relevant landmark, penalized for collisions
        rew = 0
        dists = []
        for l in world.landmarks:
            if l.id == agent.hidden_goals:
                dists.append(np.sqrt(np.sum(np.square(agent.state.p_pos - l.state.p_pos))))
                rew -= min(dists)
        if agent.collide:
            for a in world.agents:
                if self.is_collision(a, agent):
                    rew -= 1
        return rew

    def observation(self, agent, world):
        # get positions of all entities in this agent's reference frame
        entity_pos = []
        for entity in world.landmarks:  # world.entities:
            entity_pos.append(entity.state.p_pos - agent.state.p_pos)
        # entity colors
        entity_color = []
        for entity in world.landmarks:  # world.entities:
            entity_color.append(entity.color)
        # communication of all other agents
        comm = []
        other_pos = []
        for other in world.agents:
            if other is agent: continue
            comm.append(other.state.c)
            other_pos.append(other.state.p_pos - agent.state.p_pos)
        return np.concatenate([agent.state.p_vel] + [agent.state.p_pos] + entity_pos + other_pos + comm)
