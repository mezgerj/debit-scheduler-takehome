import pytest
from werkzeug.test import Client
from freezegun import freeze_time

SAMPLE_REQUEST_1 = {
    'loan': {
        'monthly_payment_amount': 750,
        'payment_due_day': 28,
        'schedule_type': 'biweekly',
        'debit_start_date': '2021-05-07',
        'debit_day_of_week': 'friday'
    }
}

SAMPLE_RESPONSE_1 = [
    {
        'today': '2021-05-07',
        'amount': 375,
        'date': '2021-05-21'
    },
    {
        'today': '2021-05-20',
        'amount': 375,
        'date': '2021-05-21'
    },
    {
        'today': '2021-05-23',
        'amount': 375,
        'date': '2021-06-04'
    },
    {
        'today': '2021-06-14',
        'amount': 375,
        'date': '2021-06-18'
    }
]

SAMPLE_REQUEST_2 = {
    'loan': {
        'monthly_payment_amount': 990,
        'payment_due_day': 1,
        'schedule_type': 'biweekly',
        'debit_start_date': '2021-05-03',
        'debit_day_of_week': 'monday'
    }
}

SAMPLE_RESPONSE_2 = [
    {
        'today': '2021-05-02',
        'amount': 330,
        'date': '2021-05-03'
    },
    {
        'today': '2021-05-12',
        'amount': 330,
        'date': '2021-05-17'
    },
    {
        'today': '2021-05-23',
        'amount': 330,
        'date': '2021-05-31'
    },
    {
        'today': '2021-06-05',
        'amount': 495,
        'date': '2021-06-14'
    }
]

SAMPLE_REQUEST_3_INVALID_DAY = {
    'loan': {
        'monthly_payment_amount': 990,
        'payment_due_day': 1,
        'schedule_type': 'biweekly',
        'debit_start_date': '2021-05-03',
        'debit_day_of_week': 'sunday'
    }
}

SAMPLE_REQUEST_4_FED_HOLIDAY = {
    'loan': {
        'monthly_payment_amount': 750,
        'payment_due_day': 1,
        'schedule_type': 'biweekly',
        'debit_start_date': '2022-01-03',
        'debit_day_of_week': 'monday'
    }
}

SAMPLE_RESPONSE_4_FED_HOLIDAY = [
    {
        'today': '2022-01-16',
        'amount': 250,
        'date': '2022-01-18'
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


def test_case_3_invalid_request(app_client):
    request = SAMPLE_REQUEST_3_INVALID_DAY

    response = app_client.post('/get_next_debit', json=request)
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid debit day provided, valid days are Mon-Fri'


@pytest.mark.parametrize('expected', SAMPLE_RESPONSE_4_FED_HOLIDAY)
def test_case_fed_holiday(app_client, expected):
    request = SAMPLE_REQUEST_4_FED_HOLIDAY

    response = app_client.post('/get_next_debit', json=request)
    with freeze_time(expected['today']):
        assert response.status_code == 200
        assert response.json['debit']['amount'] == expected['amount']
        assert response.json['debit']['date'] == expected['date']
