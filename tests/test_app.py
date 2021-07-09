import pytest
from werkzeug.test import Client
from freezegun import freeze_time


SAMPLE_REQUEST_1 = {
    'loan': {
        'monthly_payment_amount': 750,
        'payment_due_day': 28,
        'schedule_type': 'biweekly',
        'debit_start_date': '05/07/2021',
        'debit_frequency': 'friday'
    }
}

SAMPLE_RESPONSE_1 = [
    {
        'today': '05/07/21',
        'amount': 375,
        'date': '05/07/21'
    },
    {
        'today': '05/20/21',
        'amount': 375,
        'date': '05/21/21'
    },
    {
        'today': '05/23/21',
        'amount': 375,
        'date': '06/04/21'
    },
    {
        'today': '06/14/21',
        'amount': 375,
        'date': '06/18/21'
    }
]

SAMPLE_REQUEST_2 = {
    'loan': {
        'monthly_payment_amount': 990,
        'payment_due_day': 1,
        'schedule_type': 'biweekly',
        'debit_start_date': '05/03/2021',
        'debit_frequency': 'monday'
    }
}


SAMPLE_RESPONSE_2 = [
    {
        'today': '05/02/21',
        'amount': 330,
        'date': '05/03/21'
    },
    {
        'today': '05/12/21',
        'amount': 330,
        'date': '05/17/21'
    },
    {
        'today': '05/23/21',
        'amount': 330,
        'date': '05/31/21'
    },
    {
        'today': '06/05/21',
        'amount': 495,
        'date': '06/14/21'
    }
]


@pytest.fixture
def app_client():
    from app import create_app
    app = create_app()
    client = Client(app)
    return client


@pytest.mark.parametrize('expected', SAMPLE_RESPONSE_1)
def test_case_1(app_client, expected):
    request = SAMPLE_REQUEST_1

    with freeze_time(expected['today']):
        response = app_client.post('/get_next_debit', json=request)
        assert response.status_code == 200
        assert response.json['debit']['amount'] == expected['amount']
        assert response.json['debit']['date'] == expected['date']


@pytest.mark.parametrize('expected', SAMPLE_RESPONSE_2)
def test_case_2(app_client, expected):
    request = SAMPLE_REQUEST_2

    with freeze_time(expected['today']):
        response = app_client.post('/get_next_debit', json=request)
        assert response.status_code == 200
        assert response.json['debit']['amount'] == expected['amount']
        assert response.json['debit']['date'] == expected['date']
