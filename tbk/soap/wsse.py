"""
Custom implementation of wsse (without Timestamp) for TBK Webservices.

based on py-wsse suds
"""
from uuid import uuid4

import xmlsec

from .utils import create_xml_element


SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
DS_NS = "http://www.w3.org/2000/09/xmldsig#"

WSS_BASE = "http://docs.oasis-open.org/wss/2004/01/"
WSSE_NS = WSS_BASE + "oasis-200401-wss-wssecurity-secext-1.0.xsd"
WSU_NS = WSS_BASE + "oasis-200401-wss-wssecurity-utility-1.0.xsd"


def sign_envelope(envelope, key):
    """Sign given SOAP envelope with WSSE sig using given key and cert.

    Add a ds:Signature node in the wsse:Security header containing the
    signature.

    Use EXCL-C14N transforms to normalize the signed XML (so that irrelevant
    whitespace or attribute ordering changes don't invalidate the
    signature). Use SHA1 signatures.

    Expects to sign an incoming document something like this (xmlns attributes
    omitted for readability):

    <soap:Envelope>
      <soap:Header>
        <wsse:Security mustUnderstand="true">
        </wsse:Security>
      </soap:Header>
      <soap:Body>
        ...
      </soap:Body>
    </soap:Envelope>

    After signing, the sample document would look something like this (note the
    added wsu:Id attr on the soap:Body and wsu:Timestamp nodes, and the added
    ds:Signature node in the header, with ds:Reference nodes with URI attribute
    referencing the wsu:Id of the signed nodes):

    <soap:Envelope>
      <soap:Header>
        <wsse:Security mustUnderstand="true">
          <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
            <SignedInfo>
              <CanonicalizationMethod
                  Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
              <SignatureMethod
                  Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
              <Reference URI="#id-d0f9fd77-f193-471f-8bab-ba9c5afa3e76">
                <Transforms>
                  <Transform
                      Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                </Transforms>
                <DigestMethod
                    Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                <DigestValue>nnjjqTKxwl1hT/2RUsBuszgjTbI=</DigestValue>
              </Reference>
              <Reference URI="#id-7c425ac1-534a-4478-b5fe-6cae0690f08d">
                <Transforms>
                  <Transform
                      Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                </Transforms>
                <DigestMethod
                    Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                <DigestValue>qAATZaSqAr9fta9ApbGrFWDuCCQ=</DigestValue>
              </Reference>
            </SignedInfo>
            <SignatureValue>Hz8jtQb...bOdT6ZdTQ==</SignatureValue>
            <KeyInfo>
              <wsse:SecurityTokenReference>
                <X509Data>
                  <X509Certificate>MIIDnzC...Ia2qKQ==</X509Certificate>
                  <X509IssuerSerial>
                    <X509IssuerName>...</X509IssuerName>
                    <X509SerialNumber>...</X509SerialNumber>
                  </X509IssuerSerial>
                </X509Data>
              </wsse:SecurityTokenReference>
            </KeyInfo>
          </Signature>
        </wsse:Security>
      </soap:Header>
      <soap:Body wsu:Id="id-d0f9fd77-f193-471f-8bab-ba9c5afa3e76">
        ...
      </soap:Body>
    </soap:Envelope>

    """

    # Create the Signature node.
    signature = xmlsec.template.create(
        envelope, xmlsec.Transform.EXCL_C14N, xmlsec.Transform.RSA_SHA1
    )

    # Add a KeyInfo node with X509Data child to the Signature. XMLSec will fill
    # in this template with the actual certificate details when it signs.
    key_info = xmlsec.template.ensure_key_info(signature)
    x509_data = xmlsec.template.add_x509_data(key_info)
    xmlsec.template.x509_data_add_issuer_serial(x509_data)
    xmlsec.template.x509_data_add_certificate(x509_data)

    # Insert the Signature node in the wsse:Security header.
    security = get_or_create_security_header(envelope)
    security.insert(0, signature)

    # Perform the actual signing.
    ctx = xmlsec.SignatureContext()
    ctx.key = key
    sign_node(ctx, signature, envelope.find(ns(SOAP_NS, "Body")))
    ctx.sign(signature)

    # Place the X509 data inside a WSSE SecurityTokenReference within
    # KeyInfo. The recipient expects this structure, but we can't rearrange
    # like this until after signing, because otherwise xmlsec won't populate
    # the X509 data (because it doesn't understand WSSE).
    sec_token_ref = create_xml_element(ns(WSSE_NS, "SecurityTokenReference"))
    sec_token_ref.append(x509_data)
    key_info.append(sec_token_ref)


def verify_envelope(envelope, key):
    """Verify WS-Security signature on given SOAP envelope with given cert.

    Expects a document like that found in the sample XML in the ``sign()``
    docstring.

    Raise SignatureValidationFailed on failure, silent on success.

    """

    signature = get_signature_node(envelope)
    if signature is not None:
        ctx = get_signature_context(signature, envelope)
        ctx.key = key
        try:
            ctx.verify(signature)
            return True
        except xmlsec.Error:
            # Sadly xmlsec gives us no details about the reason for the failure, so
            # we have nothing to pass on except that verification failed.
            return False
    return False


def get_signature_context(signature, envelope):
    ctx = xmlsec.SignatureContext()
    # Find each signed element and register its ID with the signing context.
    refs = signature.xpath("ds:SignedInfo/ds:Reference", namespaces={"ds": DS_NS})
    for ref in refs:
        # Get the reference URI and cut off the initial '#'
        referenced_id = ref.get("URI")[1:]
        referenced = envelope.xpath(
            "//*[@wsu:Id='%s']" % referenced_id, namespaces={"wsu": WSU_NS}
        )[0]
        ctx.register_id(referenced, "Id", WSU_NS)
    return ctx


def sign_node(ctx, signature, target):
    """Add sig for ``target`` in ``signature`` node, using ``ctx`` context.

    Doesn't actually perform the signing; ``ctx.sign(signature)`` should be
    called later to do that.

    Adds a Reference node to the signature with URI attribute pointing to the
    target node, and registers the target node's ID so XMLSec will be able to
    find the target node by ID when it signs.

    """
    # Ensure the target node has a wsu:Id attribute and get its value.
    node_id = ensure_id(target)
    # Add reference to signature with URI attribute pointing to that ID.
    ref = xmlsec.template.add_reference(
        signature, xmlsec.Transform.SHA1, uri="#" + node_id
    )
    # This is an XML normalization transform which will be performed on the
    # target node contents before signing. This ensures that changes to
    # irrelevant whitespace, attribute ordering, etc won't invalidate the
    # signature.
    xmlsec.template.add_transform(ref, xmlsec.Transform.EXCL_C14N)
    # Unlike HTML, XML doesn't have a single standardized Id. WSSE suggests the
    # use of the wsu:Id attribute for this purpose, but XMLSec doesn't
    # understand that natively. So for XMLSec to be able to find the referenced
    # node by id, we have to tell xmlsec about it using the register_id method.
    ctx.register_id(target, "Id", WSU_NS)


def ns(namespace, tag_name):
    return "{%s}%s" % (namespace, tag_name)


def get_unique_id():
    return "id-{0}".format(uuid4())


def ensure_id(node):
    """Ensure given node has a wsu:Id attribute; add unique one if not.

    Return found/created attribute value.

    """
    id_attr = ns(WSU_NS, "Id")
    id_val = node.get(id_attr)
    if not id_val:
        id_val = get_unique_id()
        node.set(id_attr, id_val)
    return id_val


def get_signature_node(envelope):
    try:
        header = envelope.find(ns(SOAP_NS, "Header"))
        security = header.find(ns(WSSE_NS, "Security"))
        return security.find(ns(DS_NS, "Signature"))
    except AttributeError:
        pass
    return None


def get_or_create_header(envelope):
    tag_name = ns(SOAP_NS, "Header")
    header = envelope.find(tag_name)
    if header is None:
        header = create_xml_element(tag_name, nsmap={"wsse": SOAP_NS})
        envelope.insert(0, header)
    return header


def get_or_create_security_header(envelope):
    tag_name = ns(WSSE_NS, "Security")
    header = get_or_create_header(envelope)
    security = header.find(tag_name)
    if security is None:
        security = create_xml_element(tag_name, nsmap={"wsse": WSSE_NS})
        header.append(security)
    return security
