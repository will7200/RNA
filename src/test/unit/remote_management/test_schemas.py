from rna.modules.core.remote_management.schemas import HostCreationSchema, AuthenticationMethod


def test_host_details_model():
    host = HostCreationSchema(name='test', hostname='test', port='',
                              authentication_method='')
    assert host.port == 22
    assert host.authentication_method is None
    host1 = HostCreationSchema(name='test', hostname='test', port='222', password='asdf',
                               authentication_method=AuthenticationMethod.password)
    assert host1.port == 222
