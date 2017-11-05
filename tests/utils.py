
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


def suds2dict(d):
    """
    Suds object serializer
    Borrowed from https://stackoverflow.com/questions/2412486/serializing-a-suds-object-in-python/15678861#15678861
    """
    from suds.sudsobject import asdict
    out = {'__class__': d.__class__.__name__}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            out[k] = suds2dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(suds2dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def dict2suds(d):
    """
    Suds object deserializer
    """
    from suds.sudsobject import Factory
    out = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            out[k] = dict2suds(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if isinstance(item, dict):
                    out[k].append(dict2suds(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return Factory.object(out.pop('__class__'), out)
