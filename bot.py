#---------------------------------------------------------------------#
# Conquest Bot                                                        #
# ============                                                        #
#                                                                     #
# Last update: 26 Feb, 2014                                           #
#                                                                     #
# @author Xuj                                                         #
# @version 0.1                                                        #
# @license MIT License (http://opensource.org/licenses/MIT)           # 
#---------------------------------------------------------------------#

#---------------------------------------------------------------------#
# Handy imports:                                                      #
# +- sys                                                              #
# |`- Handles input and output                                        #
# |                                                                   #
# +- math.ceil                                                        #
# |`- Returns the ceiling of a float: the smallest int greater than   #
# |   or equal to the float                                           #
# |                                                                   #
# +- Queue.Queue                                                      #
#  `- A thread safe queue data structure, could probably also make    #
#     use of `collections.deque` instead.                             # 
#---------------------------------------------------------------------#
from math import ceil
from Queue import Queue
from sys import stdin, stdout, stderr, argv
    
#---------------------------------------#
# Main bot class                        #
#---------------------------------------#
class Bot(object):
    """
    Conquest Bot class
    """
    def __init__(self):
        """
        Constructor to set up standard values

        Tests:
        >>> bot = Bot()
        >>> bot.settings
        {}
        >>> bot.continents
        {}
        >>> bot.regions
        {}
        >>> bot.connections
        {}
        """
        # Dictionary containing game settings
        self.settings = {}

        # Dictionary containing continents and their bonus values
        self.continents = {}

        # Dictionary containing regions with their troop count, continent id and owner
        self.regions = {}

        # Dictionary containing connections between regions
        self.connections = {}
    def run(self):
        """
        Main bot loop that reads input
        """
        # Keep running until no input is given
        while not stdin.closed:

            # Try to read from stdin and do stuff with it
            try:
                
                # Read line from stdin
                rawline = stdin.readline()

                # End of file?
                if len(rawline) == 0:
                    break

                # Remove whitespace from ends of line
                line = rawline.strip()

                # Nothing in line
                if len(line) == 0:
                    continue

                # Split into parts
                parts = line.split()

                # Get command                
                cmd = parts[0]

                # Update settings
                if cmd == 'settings':
                    self.update_settings(parts[1], parts[2])

                # Set up map
                elif cmd == 'setup_map':
                    self.setup_map(parts[1:])

                # Update map
                elif cmd == 'update_map':
                    self.update_map(parts[1:])

                # Pick starting regions
                elif cmd == 'pick_starting_regions':

                    # Ignore time parameter
                    self.pick_starting_regions(parts[2:])
                    
                # Make a move
                elif cmd == 'go':

                    # Place armies
                    if parts[1] == 'place_armies':

                        # Start placing troops
                        stdout.write(self.place_troops() + '\n')

                        # Print troop placements
                        stdout.flush()

                    # attack and transfer
                    elif parts[1] == 'attack/transfer':

                        # Start transfer of troops and attack of regions
                        stdout.write(self.attack_transfer() + '\n')

                        # Print attacks/transfers
                        stdout.flush()

                # Unknown command
                else:
                    stderr.write('Unable to understand line: "%s"\n' % (line))

            # Stop when end of file is reached
            except EOFError:
                return

            # Stop when keyboard interrupt is hit (can only be done by the Godly one)
            except KeyboardInterrupt:
                print 'Ctrl-C pressed; now shutting down.'
                return

            # Stop running, damn it!!one111!
            except:
                raise
    def setup_map(self, options):
        """
        Set up game map for use

        Tests:
        >>> bot = Bot()
        >>> bot.setup_map(["super_regions", "1", "2", "2", "5"])
        >>> bot.continents[1]
        2
        >>> bot.continents[2]
        5
        >>> bot.setup_map(["regions", "1", "1", "2", "1", "3", "2", "4", "2", "5", "2"])
        >>> bot.regions[1]['continent_id']
        1
        >>> bot.regions[2]['continent_id']
        1
        >>> bot.setup_map(["neighbors", "1", "2,3,4", "2", "3", "4", "5"])
        >>> bot.connections[1]
        [2, 3, 4]
        >>> bot.connections[2]
        [1, 3]
        >>> bot.connections[3]
        [1, 2]
        >>> bot.connections[4]
        [1, 5]
        >>> bot.connections[5]
        [4]
        """
        # Get map type
        map_type = options[0]

        # Loop through options in pairs of two
        for i in range(1, len(options), 2):

            # Set up super regions (continents)
            if map_type == 'super_regions':
            
                # Get continent id
                continent_id = int(options[i])

                # Get continent bonus
                continent_bonus = int(options[i + 1])

                # Store continent into dictionary
                self.continents[continent_id] = continent_bonus

            # Set up regions
            elif map_type == 'regions':

                # Get region id
                region_id = int(options[i])

                # Get continent id
                continent_id = int(options[i + 1])

                # Store region into dictionary
                self.regions[region_id] = {
                    'owner': 'neutral',
                    'troop_count': 0,
                    'continent_id': continent_id,
                    'is_empire_border': False,
                    'is_continent_border': False
                }

            # Set up edges between countries
            elif map_type == 'neighbors':

                # Get region id
                region_id = int(options[i])

                # Get neighbour id's
                neighbour_ids = [int(n) for n in options[i + 1].split(',')]

                # Check if region id already in dictionary
                if region_id in self.connections:

                    # Append neighbour id's
                    self.connections[region_id] += neighbour_ids

                # Else create new list with neighbour id's, no need to append
                else:
                    self.connections[region_id] = neighbour_ids

                # Loop through neighbour id's
                for neighbour_id in neighbour_ids:

                    # Check if region id already in dictionary
                    if neighbour_id in self.connections:

                        # Append region_id
                        self.connections[neighbour_id] += [region_id]

                    # Else create new list with region_id, no need to append
                    else:
                        self.connections[neighbour_id] = [region_id]
                        
                # Now loop through all regions to see if they are on the edge of a continent
                for region_id in self.connections:
                    
                    # Check if this country is already on a border
                    if self.regions[region_id]['is_continent_border']:
                        continue
                    
                    # Get continent id of current region
                    continent_id = self.regions[region_id]['continent_id']
                    
                    # Loop through neighbouring countries:
                    for neighbour_id in self.get_neighbours(region_id):
                    
                        # Check continent id
                        if self.regions[neighbour_id]['continent_id'] != continent_id:
                            self.regions[region_id]['is_continent_border'] = True
                            self.regions[neighbour_id]['is_continent_border'] = True
                            
    def update_map(self, options):
        """
        Update game map to reflect new situation

        Tests:
        >>> bot = Bot()
        >>> bot.setup_map(["super_regions", "1", "2", "2", "5"])
        >>> bot.setup_map(["regions", "1", "1", "2", "1", "3", "2", "4", "2", "5", "2"])
        >>> bot.setup_map(["neighbors", "1", "2,3,4", "2", "3", "4", "5"])
        >>> bot.update_map(["1", "bot1", "2", "2", "bot1", "4", "3", "neutral", "2", "4", "bot2", "5"])
        >>> bot.regions[1]["owner"]
        'bot1'
        >>> bot.regions[1]["troop_count"]
        2
        >>> bot.regions[2]["owner"]
        'bot1'
        >>> bot.regions[2]["troop_count"]
        4
        >>> bot.regions[3]["owner"]
        'neutral'
        >>> bot.regions[3]["troop_count"]
        2
        >>> bot.regions[4]["owner"]
        'bot2'
        >>> bot.regions[4]["troop_count"]
        5
        """
        # Loop through options
        for i in range(0, len(options), 3):
        
            # Get region id
            region_id = int(options[i])

            # Get region owner
            region_owner = options[i + 1]
            
            # Get region troop count
            region_troop_count = int(options[i + 2])

            # Update region
            self.regions[region_id]['owner'] = region_owner
            self.regions[region_id]['troop_count'] = region_troop_count
            
    def update_settings(self, key, value):
        """
        Update game settings

        Tests:
        >>> bot = Bot()
        >>> bot.update_settings("time", 4000)
        >>> bot.settings["time"]
        4000
        >>> bot.update_settings("your_bot", "Teemo")
        >>> bot.settings["your_bot"]
        'Teemo'
        """
        # Set key to value
        self.settings[key] = value
    def pick_starting_regions(self, options):
        """
        Pick starting regions based on two sorting attributes:
         - Reward
         - Pickable regions in continent / total regions in continent

        Tests:
        >>> bot = Bot()
        >>> bot.setup_map(["super_regions", "1", "2", "2", "5", "3", "8"])
        >>> bot.setup_map(["regions", "1", "1", "2", "1", "3", "2", "4", "2", "5", "2", "6", "3"])
        >>> bot.setup_map(["neighbors", "1", "2,3,4", "2", "3", "4", "5,6"])
        >>> bot.pick_starting_regions(["1", "2", "3", "4", "5", "6"])
        '6 3 4 5 1 2'
        >>> bot2 = Bot()
        >>> bot2.setup_map(["super_regions", "1", "5", "2", "2", "3", "5", "4", "3", "5", "7", "6", "2"])
        >>> bot2.setup_map(["regions", '1', '1', '2', '1', '3', '1', '4', '1', '5', '1', '6', '1', '7', '1', '8', '1', '9', '1', '10', '2', '11', '2', '12', '2', '13', '2', '14', '3', '15', '3', '16', '3', '17', '3', '18', '3', '19', '3', '20', '3', '21', '4', '22', '4', '23', '4', '24', '4', '25', '4', '26', '4', '27', '5', '28', '5', '29', '5', '30', '5', '31', '5', '32', '5', '33', '5', '34', '5', '35', '5', '36', '5', '37', '5', '38', '5', '39', '6', '40', '6', '41', '6', '42', '6'])
        >>> bot2.setup_map(["neighbors", '1', '2,4,30', '2', '4,3,5', '3', '5,6,14', '4', '5,7', '5', '6,7,8', '6', '8', '7', '8,9', '8', '9', '9', '10', '10', '11,12', '11', '12,13', '12', '13,21', '14', '15,16', '15', '16,18,19', '16', '17', '17', '19,20,27,32,36', '18', '19,20,21', '19', '20', '20', '21,22,36', '21', '22,23,24', '22', '23,36', '23', '24,25,26,36', '24', '25', '25', '26', '27', '28,32,33', '28', '29,31,33,34', '29', '30,31', '30', '31,34,35', '31', '34', '32', '33,36,37', '33', '34,37,38', '34', '35', '36', '37', '37', '38', '38', '39', '39', '40,41', '40', '41,42', '41', '42'])
        >>> bot2.pick_starting_regions(["5", "3", "11", "12", "16", "18", "26", "25", "31", "38", "42", "41"])
        '11 12 42 41 26 25'
        """
        # Set up dictionary to count starting regions per continent
        region_count = {}

        # Set up dictionary to hold total region count per continent
        total_region_count = {}

        # Loop through continents to set up keys
        for key in self.continents.keys():

            # Set count to zero
            region_count[key] = 0

            # Set total count to zero
            total_region_count[key] = 0

        # Loop through every region
        for region_id in self.regions:
            total_region_count[self.regions[region_id]['continent_id']] += 1

        # Loop through options
        for option in options:
            option = int(option)
            # Get continent
            if option not in self.regions:
                return self.regions
            continent_id = self.regions[option]['continent_id']

            # Increment region count for continent by one
            region_count[continent_id] += 1

        # Get sorted representation of region_count
        sorted_count = sorted(
            region_count.items(),
            key = lambda x: (float(x[1]) / total_region_count[x[0]], self.continents[x[0]]),
            reverse = True
        )
   
        # Initialize picking regions list
        picked_regions = []

        # Loop through sorted pairs
        for pair in sorted_count:

            # Loop through regions
            for region_id in options:

                # Check if continent is current one
                if self.regions[int(region_id)]['continent_id'] == pair[0]:

                    # Append to picked_regions
                    picked_regions.append(int(region_id))
            
        # Return list
        return ' '.join([str(region) for region in picked_regions[:6]])
    def place_troops(self):
        """
        Place troops in the needed countries

        Tests:
        >>> bot = Bot()
        >>> bot.update_settings("your_bot", "bot_1")
        >>> bot.update_settings("starting_armies", "5")
        >>> bot.setup_map(["super_regions", "1", "5", "2", "2", "3", "5", "4", "3", "5", "7", "6", "2"])
        >>> bot.setup_map(["regions", '1', '1', '2', '1', '3', '1', '4', '1', '5', '1', '6', '1', '7', '1', '8', '1', '9', '1', '10', '2', '11', '2', '12', '2', '13', '2', '14', '3', '15', '3', '16', '3', '17', '3', '18', '3', '19', '3', '20', '3', '21', '4', '22', '4', '23', '4', '24', '4', '25', '4', '26', '4', '27', '5', '28', '5', '29', '5', '30', '5', '31', '5', '32', '5', '33', '5', '34', '5', '35', '5', '36', '5', '37', '5', '38', '5', '39', '6', '40', '6', '41', '6', '42', '6'])
        >>> bot.setup_map(["neighbors", '1', '2,4,30', '2', '4,3,5', '3', '5,6,14', '4', '5,7', '5', '6,7,8', '6', '8', '7', '8,9', '8', '9', '9', '10', '10', '11,12', '11', '12,13', '12', '13,21', '14', '15,16', '15', '16,18,19', '16', '17', '17', '19,20,27,32,36', '18', '19,20,21', '19', '20', '20', '21,22,36', '21', '22,23,24', '22', '23,36', '23', '24,25,26,36', '24', '25', '25', '26', '27', '28,32,33', '28', '29,31,33,34', '29', '30,31', '30', '31,34,35', '31', '34', '32', '33,36,37', '33', '34,37,38', '34', '35', '36', '37', '37', '38', '38', '39', '39', '40,41', '40', '41,42', '41', '42'])
        >>> bot.pick_starting_regions(["5", "3", "11", "12", "16", "18", "26", "25", "31", "38", "42", "41"])
        '11 12 42 41 26 25'
        >>> bot.update_map(["1", "bot1", "2", "2", "bot1", "4", "3", "neutral", "2", "4", "bot2", "5"])
        >>> bot.place_troops()
        'bot_1 place_armies 1 5'
        >>> bot.regions.itervalues().next()['troop_count']
        2
        """
        # List to hold placements
        placements = []
        
        # Loop through all our regions
        for region_id in self.regions.iterkeys():

            # Check if troops remain to be placed
            if self.settings['starting_armies'] < 1:
                break
        
            # Get neighbours
            neighbours = self.get_neighbours(region_id)
        
            # Check if this is the empire border
            self.regions[region_id]['is_empire_border'] = len([neighbour for neighbour in neighbours if self.regions[neighbour]['owner'] != self.settings['your_bot']]) == 0
        
            # If it's not the empire border, continue
            if not self.regions[region_id]['is_empire_border']:
                continue
            
            # Get enemies
            enemies = [enemy for enemy in neighbours if self.regions[enemy]['owner'] == self.settings['opponent_bot']]
            
            # Get enemy troop counts in sorted order
            enemy_troop_counts = sorted([self.regions[enemy]['troop_count'] for enemy in enemies])
            
            # Get total enemy troop count
            total_enemy_troop_count = sum(enemy_troop_counts)
            
            # Get total difference
            total_troop_difference = self.regions[region_id]['troop_count'] - total_enemy_troop_count
            
            # Calculate troops needed to defeat current region
            troops_needed_to_defeat_region = self.calculate_needed_troops(self.regions[region_id]['troop_count'])
            
            # Check if the enemy can destroy us using their current army
            if total_enemy_troop_count >= troops_needed_to_defeat_region:
                
                # Calculate troops needed to defend
                troops_needed_to_defend = self.calculate_defending_troops(total_enemy_troop_count)
                
                # Calculate difference between needed troops and available troops
                troop_difference = troops_needed_to_defend - self.regions[region_id]['troop_count']
                
                # Calculate troops needed
                needed_troops = self.settings['starting_armies'] - troop_difference
                
                # Check if we have troops to spare, else this region is lost
                if needed_troops >= 0:
                    
                    # Place troops
                    placements.append((self.settings['your_bot'], region_id, needed_troops))
                    
                    # Deduct troops
                    self.settings['starting_armies'] -= needed_troops
                    
            # We can hold
            else:
                
                # Loop through enemies
                for enemy_troop_count in enemy_troop_counts:
                    
                    # Calculate troops needed to attack
                    troops_needed_to_destroy_enemy_count = self.calculate_needed_troops(enemy_troop_count)
                    
                    # Get difference
                    troop_difference = troops_needed_to_destroy_enemy_count - self.regions[region_id]['troop_count']
                    
                    # Check if we have troops to spare, else this region is lost
                    if troop_difference <= self.settings['starting_armies']:
                        
                        # Place troops
                        placements.append((self.settings['your_bot'], region_id, troop_difference))
                        
                        # Deduct troops
                        self.settings['starting_armies'] -= troop_difference
        
        # Check if troops remain
        if self.settings['starting_armies'] > 0:
        
            # Get continent to conquer
            # Still doing this
            pass
                
        # Return the move we did
        return ', '.join(['%s place_armies %s %s' % (placement[0], placement[1], placement[2]) for placement in placements])
    def attack_transfer(self):
        """
        Attack with countries and transfer unneeded troops
        to better locations
        """
        # Get all regions with 2 troops or more
        regions = [region for region in self.region.items() if region[1]['troop_count'] > 1]
        
        # Get all regions with that aren't on the empire border
        non_border_regions = [region for region in regions if not region[1]['is_empire_border']]
        
        # Attacks and transfers
        attacks = []
        
        # Loop through regions and see whether we can attack
        for region in regions:
        
            # Find enemies in sight
            enemies = [enemy for enemy in self.get_neighbours(region[0]) if self.regions[enemy]['owner'] == self.settings['opponent_bot']]
            
            # Get normal neighbours
            neighbours = [neighbour for neighbour in self.get_neighbours(region[0]) if neighbour not in enemies and self.regions[neighbour]['owner'] != self.settings['your_bot']]
            
            # Get neighbours on current continent
            neighbours_on_continent = [neighbour for neighbour in neighbours if self.regions[neighbour]['continent_id'] == region[1]['continent_id']]
            
            # Get neighbours not on current continent
            remaining_neighbours = [neighbour for neighbour in neighbours if neighbour not in neighbours_on_continent]

            # Loop through different lists
            for category_regions in [enemies, neighbours_on_continent, neighbours_off_continent]:
                
                # Loop through all regions in given list
                for region_id in category_regions:
                    
                    # Check if we have troops left
                    if region[1]['troop_count'] < 2:
                        break                    
                    
                    # Calculate troops needed to defeat
                    troops_needed = self.calculate_troops_needed(self.regions[region_id])
                    
                    # Check if we can beat this
                    if region[1]['troop_count'] > troops_needed:
                        
                        # Add attack
                        attacks.append((self.settings['your_bot'], region[0], region_id, troops_needed))
                        
                        # Remove used troops
                        region[1]['troop_count'] -= troops_needed
        
        # Loop through non-border regions to transfer troops
        for region in non_border_regions:
            
            # Get neighbours that are on the empire border
            neighbours = [neighbour for neighbour in self.get_neighbours(region[0]) if self.regions[neighbour]['is_empire_border']]
            
            # Loop through neighbours
            for neighbour in neighbours:
            
                # Transfer all armies to empire border
                attacks.append((self.settings['your_bot'], region[0], neighbour, region[1]['troop_count'] - 1))
                
                # Remove troops
                region[1]['troop_count'] = 1
                
                # Stop after first neighbour
                break
        
        # Join attacks and return the string
        return ', '.join(['%s attack/transfer %s %s %s' % (attack[0], attack[1], attack[2], attack[3]) for attack in attacks])
    def calculate_troops_needed(self, defending_troops):
        """
        Returns the average number of troops needed to defeat the given
        amount of defending troops.

        Tests:
        >>> bot = Bot()
        >>> bot.calculate_troops_needed(2)
        4
        >>> bot.calculate_troops_needed(5)
        9
        >>> bot.calculate_troops_needed(100)
        167
        """
        return int(ceil(defending_troops / 0.6))
    def calculate_defending_troops(self, attacking_troops):
        """
        Returns the average number of troops needed to guard against the
        given amount of attack troops.
        
        Tests:
        >>> bot = Bot()
        >>> bot.calculate_defending_troops(2)
        2
        >>> bot.calculate_defending_troops(5)
        3
        >>> bot.calculate_defending_troops(100)
        60
        """
        return int(ceil(attacking_troops * 0.6))
    def get_neighbours(self, region_id):
        """
        Returns all neighbouring region id's connected to a given region

        Tests:
        >>> bot = Bot()
        >>> bot.setup_map(["super_regions", "1", "1", "2", "2"])
        >>> bot.setup_map(["regions", "1", "1", "2", "1", "3", "2", "4", "2", "5", "2"])
        >>> bot.setup_map(["neighbors", "1", "2,3,4", "2", "3", "4", "5"])
        >>> bot.get_neighbours(1)
        [2, 3, 4]
        >>> bot.get_neighbours(4)
        [1, 5]
        >>> bot.get_neighbours(5)
        [4]
        """
        # Check if node exists in graph
        if region_id in self.regions:

            # Return all neighbours
            return self.connections[region_id]

        # Return no neighbours
        return []
    def get_second_degree_neighbours(self, region_id):
        """
        Returns all region id's within a distance 2 of given region id

        Tests:
        >>> bot = Bot()
        >>> bot.setup_map(["super_regions", "1", "1", "2", "2"])
        >>> bot.setup_map(["regions", "1", "1", "2", "1", "3", "2", "4", "2", "5", "2"])
        >>> bot.setup_map(["neighbors", "1", "2,3,4", "2", "3", "4", "5"])
        >>> bot.get_second_degree_neighbours(1)
        [2, 3, 4, 5]
        >>> bot.get_second_degree_neighbours(3)
        [1, 2, 4]
        >>> bot.get_second_degree_neighbours(5)
        [1, 4]
        """
        # Get all first degree neighbours
        first_degree_neighbours = self.get_neighbours(region_id)

        # Second degree neighbour holder
        second_degree_neighbours = set(first_degree_neighbours)

        # From those, also get the first degree neighbours
        for neighbour in first_degree_neighbours:
            second_degree_neighbours |= set(self.get_neighbours(neighbour))

        # Check if node is in set, mostly to check for non-existing nodes in the current graph
        if region_id in second_degree_neighbours:

            # Remove to prevent errors
            second_degree_neighbours.remove(region_id)

        # Return the list
        return list(second_degree_neighbours)
    def breadth_first_search(self, start, end):
        """
        Returns shortest path between two nodes

        Tests:
        >>> bot = Bot()
        >>> bot.setup_map(["super_regions", "1", "1", "2", "2"])
        >>> bot.setup_map(["regions", "1", "1", "2", "1", "3", "2", "4", "2", "5", "2"])
        >>> bot.setup_map(["neighbors", "1", "2,3,4", "2", "3", "4", "5"])
        >>> bot.breadth_first_search(1, 1)
        [1]
        >>> bot.breadth_first_search(1, 4)
        [1, 4]
        >>> bot.breadth_first_search(1, 5)
        [1, 4, 5]
        >>> bot.breadth_first_search(2, 5)
        [2, 1, 4, 5]
        """
        # Set up queue
        queue = Queue()

        # Current path
        path = [start]

        # Put start into queue
        queue.put(path)

        # Visited set of nodes
        visited = set([start])

        # Start exhausting queue
        while not queue.empty():

            # Get path
            path = queue.get()

            # Get last node in path
            last_node = path[-1]
        
            # Check if done
            if last_node == end:
                return path

            # Go through edges
            for linked_node in self.connections[last_node]:

                # Check if not already visited
                if linked_node not in visited:

                    # Add to visited nodes
                    visited.add(linked_node)

                    # Add to queue
                    queue.put(path + [linked_node])

        # Return empty list in case of no path
        return []

# If not used as external module, run the following lines of code
if __name__ == '__main__':

    # Check for test mode
    if len(argv) > 1 and argv[1] == '--run-tests':
    
        # Import the testmod from Python doctest 
        from doctest import testmod
        
        # Run tests
        testmod()

    # Not testing; initialize and kick butt
    else:
    
        # Go
        Bot().run()
