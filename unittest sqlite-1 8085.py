import unittest
import requests
import random
import string
from parameterized import parameterized

base_url = "http://127.0.0.1:"
expected_response = 200
expected_meta_result = {
    "@context": {
        "@schema": "SQLite"
    },
    "video_games1": "Title,Features.Handheld?,Features.Max Players,Features.Multiplatform,Features.Online?,Metadata.Genres,Metadata.Licensed?,Metadata.Publishers,Metadata.Sequel?,Metrics.Review Score,Metrics.Sales,Metrics.Used Price,Release.Console,Release.Rating,Release.Re-release?,Release.Year,Length.All PlayStyles.Average,Length.All PlayStyles.Leisure,Length.All PlayStyles.Median,Length.All PlayStyles.Polled,Length.AllPlayStyles.Rushed,Length.Completionists.Average,Length.Completionists.Leisure,Length.Completionists.Median,Length.Completionists.Polled,Length.Completionists.Rushed,Length.Main + Extras.Average,Length.Main + Extras.Leisure,Length.Main + Extras.Median,Length.Main + Extras.Polled,Length.Main + Extras.Rushed,Length.Main Story.Average,Length.Main Story.Leisure,Length.Main Story.Median,Length.Main Story.Polled,Length.Main Story.Rushed",
}
port = 8085
database = 'SQLite'
data_type = 'video_games'
expected_schema = f"{database}/{data_type}"


def get_response(base_url, port, option):
    url_meta = base_url + str(port) + option
    return requests.get(url_meta)


class TestAPIMethods(unittest.TestCase):
    def test_get_meta(self):
        response = get_response(base_url, port, '/get_meta')
        self.assertEqual(response.status_code, expected_response)
        #self.assertEqual(response.json(), expected_meta_result)
        response_json = response.json()
        self.assertIsInstance(response_json, dict)
        self.assertIn("@context", response_json)
        self.assertIn("@schema", response_json["@context"])
        self.assertEqual(response_json["@context"]["@schema"], database)
        self.assertIn(data_type+'1', response_json)
        self.assertIsInstance(response_json[data_type+'1'], str)        # +1 because data_type in is video_games1 in for get_meta

    @parameterized.expand([('video_games', 'true'),
                           ('video_games', 'false'),
                           ('video_games', 'random'),
                           ('video_games', ''),
                           ('random', 'true'),
                           ('random', 'false'),
                           ('random', 'random'),
                           ('random', ''),
                           ('VIDEO_GAMES', 'true'),
                           ('video_games', 'FALSE')
                           ])
    def test_get_data(self, data_type, snippet):
        if data_type == 'random':
            data_type = ''.join(random.choices(string.ascii_letters, k=5))
        if snippet == 'random':
            snippet = ''.join(random.choices(string.ascii_letters, k=5))
        response = get_response(
            base_url, port, '/get_data?data_type=' + data_type + '&snippet=' + snippet)
        if (snippet == 'false' or snippet == 'true') and data_type == 'video_games':
            self.assertEqual(response.status_code, expected_response)
            self.assertEqual(
                response.json()['@context']['@schema'], expected_schema)

            # Check that @list contains at least 20 element for snippet = false or only 20 for snippet = true
            if snippet == 'false':
                self.assertGreater(len(response.json()['@list']), 20)
            else:
                self.assertEqual(len(response.json()['@list']), 20)

            # Check that @list contains no more than 30% null values
            for element in response.json()['@list']:
                # Check that all keys from @list exists and none are missing
                metadata = "@id,Title,Features.Handheld?,Features.Max Players,Features.Multiplatform,Features.Online?,Metadata.Genres,Metadata.Licensed?,Metadata.Publishers,Metadata.Sequel?,Metrics.Review Score,Metrics.Sales,Metrics.Used Price,Release.Console,Release.Rating,Release.Re-release?,Release.Year,Length.All PlayStyles.Average,Length.All PlayStyles.Leisure,Length.All PlayStyles.Median,Length.All PlayStyles.Polled,Length.AllPlayStyles.Rushed,Length.Completionists.Average,Length.Completionists.Leisure,Length.Completionists.Median,Length.Completionists.Polled,Length.Completionists.Rushed,Length.Main + Extras.Average,Length.Main + Extras.Leisure,Length.Main + Extras.Median,Length.Main + Extras.Polled,Length.Main + Extras.Rushed,Length.Main Story.Average,Length.Main Story.Leisure,Length.Main Story.Median,Length.Main Story.Polled,Length.Main Story.Rushed",
                # Convert keys tuple into a list of keys
                keys_list_metadata = list(metadata)
                # Split the string above in invidual keys inside list
                keys_list_metadata = str.split(keys_list_metadata[0], ',')
                keys_list_element = list(element.keys())
                # Transform lists into arrays
                arr_meta = [sub.split() for sub in keys_list_metadata]
                arr_elem = [sub.split() for sub in keys_list_element]
                # Display array
                self.assertTrue(len(arr_meta) == len(
                    arr_elem), "Metadata and properties of elements from @list are not the same")
                for i in range(len(arr_meta)):
                    self.assertTrue(arr_meta[i] == arr_elem[i], "Metadata and properties of elements from @list are not the same for" + str(
                        arr_elem[i]) + ' ' + str(arr_meta[i]))

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
