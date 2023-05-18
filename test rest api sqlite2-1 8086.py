import unittest
import requests
import random
import string
from parameterized import parameterized

base_url = "http://127.0.0.1:"
expected_response = 200
port = 8565     #8086
database = 'SQLite'
data_type: str
expected_schema = str
expected_meta_result = {
        "@context": {
            "@schema": "SQLite"
        },
        "video_games": "Id,Name,Platform,Release Year,Genre,Publisher,North America Sales,Europe Sales,Japan Sales,Other Sales,Global Sales,Critic Score,Critic Count,User Score,User Count,Developer,Rating",
        "consoles": "Id,Name,Manufacturer,Release Year,Units Sold (millions),Type,Number of Exclusives,Processing Unit Type,CPU Equivalent,CPU Frequency,GPU Equivalent,RAM Size,RAM Frequency",
        "mice": "Id,Manufacturer,Model,Resolution,Design,Number of buttons,Interface,Weight,Size,Rating,Link address,Battery,Use,Extra Functions",
        "CPU": "Model,Manufacturer,Family,Codename,Release Year,Discontinued,Base Clock,Boost Clock,Sockets,L1 Cache Size,L2 Cache Size,Process Size (nm),Number of Cores,Number of Threads,TDP,System Memory Type,System Memory Frequency,Instruction Set,Maximum Operating Temperature,Launch Price ($)",
        "GPU": "Model,Manufacturer,Release Year,Discontinued,Graphics Processor,Transistors (millions),Process Size (nm),Shading Units,Core Base Clock,Core Boost Clock,Memory Type,Memory Size,Memory Bandwidth,Memory Clock Speed (Effective),TDP,Display Outputs,Cooling System,Cooling Type,DirectX,OpenGL,OpenCL,Vulkan,Shader Model,CUDA,Launch Price ($)"
}


# Function to get response for a request
def get_response(base_url, port, option):
    url_meta = base_url + str(port) + option
    return requests.get(url_meta)


# Check if list list1 is a subset of list2
def check_if_subset(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    return set1.issubset(set2)

# Check if a list has duplicates
def check_for_duplicates(list):
    return len(list) == len(set(list))


class TestAPI(unittest.TestCase):
    # test get_meta response
    def test_get_meta(self):
        response = get_response(base_url, port, '/get_meta')
        self.assertEqual(response.status_code, expected_response)
        self.assertEqual(response.json(), expected_meta_result)


    # test get_predictions responses
    @parameterized.expand([('consoles', '1970,1990,2000,2010,2020,2000'),
                           ('CPU', '1970,1990,2000,2010,2020,2000')     ,
                           ('GPU', '1970,1990,2000,2010,2020,2000')     ,
                           ('Consoles', '1970,1990,2000,2010,2020,2000'),
                           ('cpu', '1970,1990,2000,2010,2020,2000')     ,
                           ('gpu', '1970,1990,2000,2010,2020,2000')     ,
                           ('', '1970,1990,2000,2010,2020,2000')        ,
                           ('consoles', ''),    ('CPU', ''),    ('GPU', ''),    ('', '')])
    def test_predictions(self, data_type, years):
        response = get_response(
            base_url, port, '/get_prediction?data_type=' + data_type + '&years=' + years)

        data_types = ['CPU', 'GPU', 'consoles']        # define array that stores data types 
        expected_schema = f"{database}/{data_type}"
        if years == '' or data_type not in data_types:
            self.assertNotEqual(response.status_code, expected_response)
        
        else:
            # Check that @list contains the same field as the one for predictions and not duplicates for years
            self.assertEqual(response.json()['@context']['@schema'], expected_schema)
            response_years = []
            request_years  = [int(x) for x in years.split(',')]

            for element in response.json()['@list']:
                property_count = len(element.keys())

                if data_type == 'consoles':
                    self.assertEqual(property_count, 9)
                    self.assertGreaterEqual(element['Release Year'], 1985)
                elif data_type == 'CPU':
                    self.assertEqual(property_count, 12)
                    self.assertGreaterEqual(element['Release Year'], 1975)
                else:
                    self.assertEqual(property_count, 12)
                    self.assertGreaterEqual(element['Release Year'], 1990)

                response_years.append(element['Release Year'])
            
            self.assertEqual(check_if_subset(response_years, request_years), True)
            self.assertEqual(check_for_duplicates(response_years), True)


    # test get_data responses
    @parameterized.expand([('video_games', 'true')  ,                   ('video_games', 'false'),
                           ('video_games', 'random'),                   ('video_games', '')     ,
                           ('VIDEO_GAMES', 'true')  ,                   ('video_games', 'FALSE'),
                           ('consoles', 'true')     ,                   ('consoles', 'false')   ,
                           ('consoles', 'random')   ,                   ('consoles', '')        ,
                           ('CONSOLES', 'true')     ,                   ('CONSOLES', 'FALSE')   ,
                           ('mice', 'true')         ,                   ('mice', 'false')       ,
                           ('mice', 'random')       ,                   ('mice', '')            ,
                           ('MICE', 'true')         ,                   ('mice', 'FALSE')       ,
                           ('CPU', 'true')          ,                   ('CPU', 'false')        ,
                           ('CPU', 'random')        ,                   ('CPU', '')             ,
                           ('cpu', 'true')          ,                   ('CPU', 'FALSE')        ,
                           ('GPU', 'true')          ,                   ('GPU', 'false')        ,
                           ('GPU', 'random')        ,                   ('GPU', '')             ,
                           ('gpu', 'true')          ,                   ('GPU', 'FALSE')        ,
                           ('random', 'true')       ,                   ('random', 'false')     ,
                           ('random', 'random')     ,                   ('random', '')          ,
                           ('', 'false')            ,                   ('', 'true')            ,
                           ('', '')])
    def test_get_data(self, data_type, snippet):
        if data_type == 'random':
            # generate a random data_type for the test where data_type = random
            data_type = ''.join(random.choices(string.ascii_letters, k=5))
        if snippet == 'random':
            # generate a random snippet for the test where snippet = random
            snippet = ''.join(random.choices(string.ascii_letters, k=5))
        response = get_response(
            base_url, port, '/get_data?data_type=' + data_type + '&snippet=' + snippet)

        data_types = ['video_games', 'mice', 'CPU', 'GPU', 'consoles']        # define array that stores data types 
        expected_schema = f"{database}/{data_type}"
        if (snippet == 'false' or snippet == 'true') and data_type in data_types:
            self.assertEqual(response.status_code, expected_response)
            self.assertEqual(response.json()['@context']['@schema'], expected_schema)

            # Check that @list contains at least 20 element for snippet = false or only 20 for snippet = true
            if snippet == 'false':
                self.assertGreater(len(response.json()['@list']), 20)
            else:
                self.assertEqual(len(response.json()['@list']), 20)

            # Check that @list contains no more than 30% null values
            for element in response.json()['@list']:
                null_property_count = 0
                property_count = len(element.keys())
                for k in element.keys():                                    # null is interpreted as None
                    if element[k] is None:
                        null_property_count += 1
                # make sure there are less than 30% None values for items
                self.assertLessEqual(null_property_count / property_count, 0.3)
        else:
            # Check the content of the response
            self.assertNotEqual(response.status_code, expected_response)


if __name__ == '__main__':
    unittest.main()
