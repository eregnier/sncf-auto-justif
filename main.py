import os
import json
import requests
import time
import logging
import datetime
from dotenv import load_dotenv
from pyquery import PyQuery as pq
from slugify import slugify

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename="data/sncf.log",
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
db_path = 'data/db.json'


def get_db():
    if os.path.isfile(db_path):
        with open(db_path) as f:
            return set(json.load(f))
    else:
        return set()


def save_db(db):
    with open(db_path, "w") as f:
        f.write(json.dumps(list(db), indent=4))


def login(session):
    """The session instance holds the cookie. So use it to get/post later."""
    email = os.environ.get('EMAIL')
    password = os.environ.get('PASS')
    session.get(
        "https://oui.sncf",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response = session.post(
        "https://www.oui.sncf/customer/api/clients/customer/authentication",
        headers={"User-Agent": "Mozilla/5.0"},
        json={
            "email": email,
            "redirectUri": "https://www.oui.sncf/espaceclient/authentication/consumeCode",
            "state": "https://www.oui.sncf"
        }
    )
    print('send login code', response.status_code)
    print('send login content', response.text)

    response = session.post(
        "https://www.oui.sncf/espaceclient/authentication/flowSignIn",
        headers={"User-Agent": "Mozilla/5.0"},
        data={
            "lang": "fr",
            "login": email,
            "password": password,
        }
    )

    print(f'Send password code {response.status_code}')
    print(f'Send password content {response.text}')


def fetch_justificatory(session):
    response = session.get(
        'https://www.oui.sncf/espaceclient/ordersconsultation/showOrdersForAjaxRequest',
        params={
            "pastOrder": "true",
            "cancelledOrder": "false",
            "pageToLoad": "1",
            "_": str(int(time.time() * 1000))
        }
    )
    print('Justificatory reponse code {}'.format(response.status_code))
    assert response.status_code == 200
    return response.text


def parse_justificatory(justificatory, db):
    d = pq(justificatory)
    for ticket in d('.small-collapse'):
        ticket_id = d(ticket)('.order__detail [data-auto="ccl_orders_travel_number"]').text()
        if ticket_id not in db:
            link = d(ticket).find('a').attr('href')
            date = slugify(d(ticket).find('.texte--droite').text())
            print(date.split('.')[0])
            if '/vsc/aftersale' in link:
                try:
                    filepath = f'data/{ticket_id}-{date}.pdf'
                    response = requests.get(link)
                    assert response.status_code == 200
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    db.add(ticket_id)
                except Exception as e:
                    logging.error(f"Impossible de récupérer le justificatif {ticket_id} du {ticket_date}")
                    logging.debug(e)
            else:
                logging.info("Ticket non disponible : %s", ticket_id)


if __name__ == "__main__":
    db = get_db()
    session = requests.Session()
    login(session)
    justificatory = fetch_justificatory(session)
    start_len = len(db)
    parse_justificatory(justificatory, db)
    delta = len(db) - start_len
    if delta:
        print(f'{delta} nouveaux justificatifs téléchargés')
    save_db(db)
