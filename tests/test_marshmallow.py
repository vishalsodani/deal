import marshmallow
import vaa

import deal
import pytest


@pytest.fixture()
def scheme():
    class _Scheme(marshmallow.Schema):
        name = marshmallow.fields.Str()
    yield vaa.marshmallow(_Scheme)


def test_scheme_string_validation_args_correct(scheme):
    @deal.pre(scheme)
    def func(name):
        return name * 2

    assert func('Chris') == 'ChrisChris'

    with pytest.raises(deal.PreContractError):
        func(123)

    try:
        func(123)
    except deal.PreContractError as e:
        assert e.args[0] == {'name': ['Not a valid string.']}


def test_method_chain_decorator_with_scheme_is_fulfilled(scheme):
    @deal.pre(scheme)
    @deal.pre(lambda name: name != 'Oleg')
    def func(name):
        return name * 2

    assert func('Chris') == 'ChrisChris'

    with pytest.raises(deal.PreContractError):
        func(123)

    with pytest.raises(deal.PreContractError):
        func('Oleg')


def test_scheme_contract_is_satisfied_when_setting_arg(scheme):
    @deal.inv(scheme)
    class User:
        name = ''

    user = User()

    user.name = 'Chris'

    with pytest.raises(deal.InvContractError):
        user.name = 123

    try:
        user.name = 123
    except deal.InvContractError as e:
        assert e.args[0] == {'name': ['Not a valid string.']}


def test_scheme_contract_is_satisfied_within_chain(scheme):
    @deal.inv(lambda user: user.name != 'Oleg')
    @deal.inv(scheme)
    @deal.inv(lambda user: user.name != 'Chris')
    class User:
        name = ''

    user = User()
    user.name = 'Gram'

    user = User()
    with pytest.raises(deal.InvContractError):
        user.name = 'Oleg'

    user = User()
    with pytest.raises(deal.InvContractError):
        user.name = 123

    user = User()
    with pytest.raises(deal.InvContractError):
        user.name = 'Chris'


def test_scheme_contract_is_satisfied_when_passing_args(scheme):
    @deal.pre(scheme)
    def func(name):
        return name * 2

    assert func('Chris') == 'ChrisChris'

    assert func(name='Chris') == 'ChrisChris'

    @deal.pre(scheme)
    def func(**kwargs):
        return kwargs['name'] * 3

    assert func(name='Chris') == 'ChrisChrisChris'

    @deal.pre(scheme)
    def func(name='Max'):
        return name * 2

    assert func() == 'MaxMax'
