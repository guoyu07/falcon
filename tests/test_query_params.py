import falcon
import falcon.testing as testing


class TestQueryParams(testing.TestBase):

    def before(self):
        self.resource = testing.TestResource()
        self.api.add_route('/', self.resource)

    def test_none(self):
        query_string = ''
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertEquals(req.get_param('marker'), None)
        self.assertEquals(req.get_param('limit'), None)
        self.assertEquals(req.get_param_as_int('limit'), None)
        self.assertEquals(req.get_param_as_bool('limit'), None)
        self.assertEquals(req.get_param_as_list('limit'), None)

    def test_blank(self):
        query_string = 'marker='
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertEquals(req.get_param('marker'), None)

    def test_simple(self):
        query_string = 'marker=deadbeef&limit=25'
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertEquals(req.get_param('marker') or 'deadbeef', 'deadbeef')
        self.assertEquals(req.get_param('limit') or '25', '25')

    def test_required(self):
        query_string = ''
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertRaises(falcon.HTTPBadRequest, req.get_param,
                          'marker', required=True)
        self.assertRaises(falcon.HTTPBadRequest, req.get_param_as_int,
                          'marker', required=True)
        self.assertRaises(falcon.HTTPBadRequest, req.get_param_as_bool,
                          'marker', required=True)
        self.assertRaises(falcon.HTTPBadRequest, req.get_param_as_list,
                          'marker', required=True)

    def test_int(self):
        query_string = 'marker=deadbeef&limit=25'
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertRaises(falcon.HTTPBadRequest, req.get_param_as_int,
                          'marker')
        self.assertEquals(req.get_param_as_int('limit'), 25)

    def test_boolean(self):
        query_string = 'echo=true&doit=false&bogus=0&bogus2=1'
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertRaises(falcon.HTTPBadRequest, req.get_param_as_bool,
                          'bogus')
        self.assertRaises(falcon.HTTPBadRequest, req.get_param_as_bool,
                          'bogus2')

        self.assertEquals(req.get_param_as_bool('echo'), True)
        self.assertEquals(req.get_param_as_bool('doit'), False)

    def test_list_type(self):
        query_string = 'colors=red,green,blue&limit=1'
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertEquals(req.get_param('colors'), 'red,green,blue')
        self.assertEquals(req.get_param_as_list('colors'),
                          ['red', 'green', 'blue'])
        self.assertEquals(req.get_param_as_list('limit'), ['1'])
        self.assertEquals(req.get_param_as_list('marker'), None)

    def test_list_transformer(self):
        query_string = 'coord=1.4,13,15.1&limit=100'
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertEquals(req.get_param('coord'), '1.4,13,15.1')

        expected = [1.4, 13.0, 15.1]
        actual = req.get_param_as_list('coord', transform=float)
        self.assertEquals(actual, expected)

        self.assertRaises(falcon.HTTPBadRequest,
                          req.get_param_as_list, 'coord', transform=int)

    def test_bogus_input(self):
        query_string = 'colors=red,green,&limit=1&pickle'
        self.simulate_request('/', query_string=query_string)

        req = self.resource.req
        self.assertEquals(req.get_param_as_list('colors'),
                          ['red', 'green', ''])
        self.assertEquals(req.get_param('limit'), '1')
        self.assertEquals(req.get_param('pickle'), None)
