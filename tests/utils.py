
import os

from tbk.commerce import Commerce

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


def create_commerce(commerce_code):
    return Commerce.init_from_files(
        commerce_code=commerce_code,
        key_file=os.path.join(DATA_DIR, '{}.key'.format(commerce_code)),
        cert_file=os.path.join(DATA_DIR, '{}.crt'.format(commerce_code)),
        tbk_cert_file=os.path.join(DATA_DIR, 'tbk.pem'),
        environment='INTEGRACION'
    )
