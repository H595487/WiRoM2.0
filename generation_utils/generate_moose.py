import json
from wbt_json_parser import wbt_json_parser
from json_reader_writer import json_reader_writer
import pathlib


class GenerateMoose():
    def __init__(self):
        self.map_reader = wbt_json_parser()
        self.json_reader_writer = json_reader_writer()
        self.moose_template = self.read_template()
        self.configpath = pathlib.Path.cwd().parent / 'backend' / 'config.json'
        self.datapath = pathlib.Path.cwd().parent / 'web_interface' / 'src' / 'data.json'
        self.new_positions = []

    def read_template(self):
        template = self.json_reader_writer.read_json("moose_template.json")
        return template

    def test_adding_moose_to_world(self):
        new_moose_node = self.moose_template["webots_world"]["Moose"]

        self.map_reader.read_file()
        all_moose = self.map_reader.get_all_moose()

        all_translations = []

        # The "lowest transformation will be the one with the lowest z value"
        lowest_transformation = [0, 0, float('inf')]
        for x in all_moose:
            translation = self.get_translation(x)
            if translation[2] < lowest_transformation[2]:
                lowest_transformation = translation
            all_translations.append(translation)

        new_transformation = lowest_transformation
        new_transformation[2] = lowest_transformation[2] - 5
        self.new_positions = new_transformation
        # Since we converted it to floats to do calculations, we need to convert them back to string 
        new_transformation = " ".join([str(x) for x in new_transformation])

        # Update the translation on the new node
        new_moose_node["translation"] = new_transformation
        # print(f'Updated moose node: {new_moose_node}')

        # Set name TODO should be dynamic
        new_moose_node["name"] = "\"testmoose\""
        # Set the controller
        new_moose_node["controller"] = "\"void\""
        new_moose_node = {"Moose": new_moose_node}

        new_file_content = self.map_reader.transform_from_json_to_world(new_moose_node)
        self.map_reader.append_to_world_file(new_file_content)

    def get_translation(self, node):
        translation = [float(x) for x in node["translation"].split()]
        return translation

    def test_adding_moose_to_config(self):
        config_content = self.json_reader_writer.read_json(self.configpath)
        # print(f'Config content: {config_content}')

        moose_config_from_template = self.moose_template["config"]["moose"]
        if not self.new_positions:
            print("Haven't fetched the positions from the world file yet. Setting them to default 0, 0")
            new_x, new_y = 0, 0
        else:
            new_x = self.new_positions[0]
            # TODO I am currently using the z position from the translation to add to the x and y position
            new_y = self.new_positions[2]

        # Set the new positions in the node fetched from the template
        moose_config_from_template["location"] = {
            "x": new_x,
            "y": new_y
        }
        # Set the port
        new_port_number = self.find_next_port_number(config_content["robots"])
        moose_config_from_template["port"] = str(new_port_number)

        # The count of moose robots will determine the key name (which needs to be unique)
        moose_count = self.count_moose(config_content["robots"])
        key_name = "moose" + str(moose_count + 1)

        # Now append the created moose data to the "robots" sections in config
        config_content["robots"][key_name] = moose_config_from_template
        # Print it to output file
        # self.json_reader_writer.write_json("test_config.json", json.dumps(config_content, indent=2))
        self.json_reader_writer.write_json(self.configpath, json.dumps(config_content, indent=2))

    def test_adding_moose_to_data(self):
        data_content = self.json_reader_writer.read_json(self.datapath)

        moose_data_from_template = self.moose_template["data"]["moose"]

        # Add the port
        new_port_number = self.find_next_port_number(data_content["robots"])
        print(f'New port number: {new_port_number}')
        moose_data_from_template["port"] = str(new_port_number)

        # The count of moose robots will determine the key name (which needs to be unique)
        moose_count = self.count_moose(data_content["robots"])
        key_name = "moose" + str(moose_count + 1)

        data_content["robots"][key_name] = moose_data_from_template
        # self.json_reader_writer.write_json("test_data.json", json.dumps(data_content, indent=4))
        self.json_reader_writer.write_json(self.datapath, json.dumps(data_content, indent=4))

    def test_adding_moose_controller(self):
        pass

    def find_next_port_number(self, content):
        '''
        Goes through the config file, and finds all the used port numbers.
        Returns the new port number, which is the highest number previously used + 1
        '''
        largest_port_number = 0
        for value in content.values():
            # print(f'key: {key}, val: {value}')
            port = int(value["port"])
            if port > largest_port_number:
                largest_port_number = port

        return largest_port_number + 1

    def count_moose(self, content):
        count = 0
        for key in content.keys():
            if key[:5] == "moose":
                count += 1
        return count


if __name__ == "__main__":
    generate_moose = GenerateMoose()
    generate_moose.test_adding_moose_to_world()
    generate_moose.test_adding_moose_to_config()
    generate_moose.test_adding_moose_to_data()
    # generate_moose.test_adding_moose_controller()
