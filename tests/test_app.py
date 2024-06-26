import unittest
from app import app

class FlaskAppTests(unittest.TestCase):

    # Setup the test client
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Test the home route
    def test_home(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Welcome', result.data)

    # Test the random string generator route
    def test_random_string_generator(self):
        result = self.app.post('/string-tools/random-string-generator', data=dict(length=16))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Your Random String', result.data)

    # Test the random number generator route
    def test_random_number_generator(self):
        result = self.app.post('/string-tools/random-number-generator', data=dict(min_val=0, max_val=100))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Your Random Number', result.data)


    # Test the shuffle letters route
    def test_shuffle_letters(self):
        result = self.app.post('/string-tools/shuffle-letters', data=dict(text='apple'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Shuffled Text', result.data)

    # Test the clean text route
    def test_clean_text(self):
        result = self.app.post('/string-tools/clean-text', data=dict(text='This sentence has a problem.it needs help. This I know.         this is true.'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Cleaned Text', result.data)

    # Test the text statistics route
    def test_text_statistics(self):
        result = self.app.post('/string-tools/text-statistics', data=dict(text='This is a test. This is only a test.'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Text Statistics', result.data)

    # Test the column extractor route
    def test_column_extractor(self):
        text = 'Red. Apple. Small.\nYellow. Banana. Medium.\nGreen. Pea. Large.'
        result = self.app.post('/string-tools/column-extractor', data=dict(text=text, column_number=2, delimiter='.'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Extracted Columns', result.data)

    # Test the JSON validator route
    def test_json_validator(self):
        result = self.app.post('/json-tools/json-validator', data=dict(json_input='{"name": "John", "age": 30}'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'JSON is valid.', result.data)

    # Test the JSON schema generator route
    def test_json_schema_generator(self):
        result = self.app.post('/json-tools/json-schema-generator', data=dict(json_input='{"name": "John", "age": 30}'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Generated JSON Schema', result.data)

    # Test the JSON sample generator route
    def test_json_sample_generator(self):
        result = self.app.post('/json-tools/json-sample-generator', data=dict(schema_input='{"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Generated Sample JSON', result.data)


    # Test the JSON converter route
    # def test_json_converter(self):
    #     result = self.app.post('/json-tools/json-converter', data=dict(conversion_type='to_json', input_data='{"name": "John", "age": 30}'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Converted JSON', result.data)


    # Test the JSON parser route
    # def test_json_parser(self):
    #     result = self.app.post('/json-tools/json-parser', data=dict(json_input='{"name": "John", "age": 30}'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Parsed JSON', result.data)

    # Test the RegEx checker route
    def test_regex_checker(self):
        result = self.app.post('/regex-tools/regex-checker', data=dict(regex='^a.*z$', string='abcz'))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Pattern matches the string.', result.data)


    # Test the RegEx generator route
    # def test_regex_generator(self):
    #     result = self.app.post('/regex-tools/regex-generator', data=dict(pattern='abc'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Generated RegEx', result.data)

    # Test the Diff Viewer route
    # def test_diff_viewer(self):
    #     result = self.app.post('/diff-viewer', data=dict(text1='Hello world', text2='Hello'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Diff Result', result.data)

    # Test the Base64 Encoder Decoder route
    # def test_base64_encoder_decoder(self):
    #     result = self.app.post('/base64-encode-decode', data=dict(text='Hello world'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Encoded Base64', result.data)

    # Test the Character/Word Counter route
    # def test_counter(self):
    #     result = self.app.post('/counter', data=dict(text='Hello world'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Character Count', result.data)

    # Test the Time Converter route
    # def test_time_converter(self):
    #     result = self.app.post('/time-converter', data=dict(time='12:00', from_format='PM', to_format='24HR'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Converted Time', result.data)

    # Test the CRON Scheduler route
    # def test_schedule_cron(self):
    #     result = self.app.post('/schedule-cron', data=dict(cron='0 5 * * *'))
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b'Scheduled CRON', result.data)

if __name__ == '__main__':
    unittest.main()
