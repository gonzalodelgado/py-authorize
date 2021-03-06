import xml.etree.cElementTree as E

from unittest import TestCase

from authorize.response_parser import parse_response


SINGLE_LIST_ITEM_RESPONSE_XML = '''
<?xml version="1.0" ?>
<simpleResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <messages>
    <resultCode>Ok</resultCode>
    <message>
      <code>I00001</code>
      <text>Successful.</text>
    </message>
  </messages>
</simpleResponse>
'''

MULTIPLE_LIST_ITEM_RESPONSE_XML = '''
<?xml version="1.0" ?>
<simpleResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <messages>
    <resultCode>Ok</resultCode>
    <message>
      <code>I00001</code>
      <text>Successful.</text>
    </message>
  </messages>
  <messages>
    <resultCode>Ok</resultCode>
    <message>
      <code>I00001</code>
      <text>Successful.</text>
    </message>
  </messages>
</simpleResponse>
'''

NUMERIC_STRING_LIST_RESPONSE_XML = '''
<?xml version="1.0" ?>
<createCustomerProfileResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <messages>
    <resultCode>Ok</resultCode>
    <message>
      <code>I00001</code>
      <text>Successful.</text>
    </message>
  </messages>
  <customerProfileId>24527322</customerProfileId>
  <customerPaymentProfileIdList>
    <numericString>22467955</numericString>
    <numericString>22467956</numericString>
    <numericString>22467957</numericString>
  </customerPaymentProfileIdList>
  <customerShippingAddressIdList/>
  <validationDirectResponseList/>
</createCustomerProfileResponse>
'''

DIRECT_RESPONSE_XML = '''
<?xml version="1.0" ?>
<createCustomerProfileTransactionResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <messages>
    <resultCode>Ok</resultCode>
    <message>
      <code>I00001</code>
      <text>Successful.</text>
    </message>
  </messages>
  <directResponse>1,1,1,This transaction has been approved.,RUQ2CH,Y,2208147721,INV0001,Just another invoice...,695.31,CC,auth_capture,a9f25ea698324879955d,,,,,,,,,,,,,,,,,,,,45.00,90.00,10.00,FALSE,,DDE9931C84D8D4062EC36DC5E21C22AA,,2,,,,,,,,,,,XXXX1111,Visa,,,,,,,,,,,,,,,,</directResponse>
</createCustomerProfileTransactionResponse>
'''

TRANSACTION_LIST_RESPONSE_XML = '''
<?xml version="1.0" ?>
<getTransactionListResponse xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <messages>
    <resultCode>Ok</resultCode>
    <message>
      <code>I00001</code>
      <text>Successful.</text>
    </message>
  </messages>
  <transactions>
    <transaction>
      <transId>2213859708</transId>
      <submitTimeUTC>2014-05-25T08:40:21Z</submitTimeUTC>
      <submitTimeLocal>2014-05-25T01:40:21</submitTimeLocal>
      <transactionStatus>settledSuccessfully</transactionStatus>
      <firstName>Robot</firstName>
      <lastName>Ron</lastName>
      <accountType>Visa</accountType>
      <accountNumber>XXXX1111</accountNumber>
      <settleAmount>231.00</settleAmount>
      <marketType>eCommerce</marketType>
      <product>Card Not Present</product>
      <subscription>
        <id>1652905</id>
        <payNum>32</payNum>
      </subscription>
    </transaction>
    <transaction>
      <transId>2213858843</transId>
      <submitTimeUTC>2014-05-25T08:39:15Z</submitTimeUTC>
      <submitTimeLocal>2014-05-25T01:39:15</submitTimeLocal>
      <transactionStatus>settledSuccessfully</transactionStatus>
      <firstName>Robot</firstName>
      <lastName>Ron</lastName>
      <accountType>Visa</accountType>
      <accountNumber>XXXX1111</accountNumber>
      <settleAmount>4022.00</settleAmount>
      <marketType>eCommerce</marketType>
      <product>Card Not Present</product>
      <subscription>
        <id>1591888</id>
        <payNum>37</payNum>
      </subscription>
    </transaction>
  </transactions>
</getTransactionListResponse>
'''

SINGLE_LIST_ITEM_RESPONSE = {
    'messages': [{
        'result_code': 'Ok',
        'message': {
            'text': 'Successful.',
            'code': 'I00001',
        },
    }]
}

MULTIPLE_LIST_ITEM_RESPONSE = {
    'messages': [{
        'result_code': 'Ok',
        'message': {
            'text': 'Successful.',
            'code': 'I00001',
        },
    }, {
        'result_code': 'Ok',
        'message': {
            'text': 'Successful.',
            'code': 'I00001',
        },
    }]
}

NUMERIC_STRING_LIST_RESPONSE = [
    '22467955',
    '22467956',
    '22467957',
]

TRANSACTION_RESPONSE = {
    'messages': [{
        'result_code': 'Ok',
        'message': {
            'text': 'Successful.',
            'code': 'I00001',
        },
    }],
    'transaction_response': {
        'cvv_result_code': '',
        'authorization_code': 'RUQ2CH',
        'response_code': '1',
        'amount': '695.31',
        'transaction_type': 'auth_capture',
        'avs_response': 'Y',
        'response_reason_code': '1',
        'response_reason_text': 'This transaction has been approved.',
        'trans_id': '2208147721',
    }
}

TRANSACTION_LIST_RESPONSE = {
    'messages': [{
        'message': {
            'text': 'Successful.', 
            'code': 'I00001'
        }, 
        'result_code': 'Ok'
    }], 
    'transactions': [{
        'first_name': 'Robot', 
        'last_name': 'Ron', 
        'account_type': 'Visa', 
        'submit_time_local': '2014-05-25T01:40:21', 
        'product': 'Card Not Present', 
        'submit_time_utc': '2014-05-25T08:40:21Z', 
        'account_number': 'XXXX1111', 
        'market_type': 'eCommerce', 
        'transaction_status': 'settledSuccessfully', 
        'settle_amount': '231.00', 
        'trans_id': '2213859708', 
        'subscription': {
            'pay_num': '32', 
            'id': '1652905'
        }
    }, {
        'first_name': 'Robot', 
        'last_name': 'Ron', 
        'account_type': 'Visa', 
        'submit_time_local': '2014-05-25T01:39:15', 
        'product': 'Card Not Present', 
        'submit_time_utc': '2014-05-25T08:39:15Z', 
        'account_number': 'XXXX1111', 
        'market_type': 'eCommerce', 
        'transaction_status': 'settledSuccessfully', 
        'settle_amount': '4022.00', 
        'trans_id': '2213858843', 
        'subscription': {
            'pay_num': '37', 
            'id': '1591888'
        }
    }]
}


class ResponseParserTests(TestCase):

    maxDiff = None

    def test_parse_single_line_item_response(self):
        response_element = E.fromstring(SINGLE_LIST_ITEM_RESPONSE_XML.strip())
        response = parse_response(response_element)
        self.assertEquals(SINGLE_LIST_ITEM_RESPONSE, response)

    def test_parse_multiple_line_item_response(self):
        response_element = E.fromstring(MULTIPLE_LIST_ITEM_RESPONSE_XML.strip())
        response = parse_response(response_element)
        self.assertEquals(MULTIPLE_LIST_ITEM_RESPONSE, response)

    def test_parse_numeric_string_response(self):
        response_element = E.fromstring(NUMERIC_STRING_LIST_RESPONSE_XML.strip())
        response = parse_response(response_element)
        self.assertEquals(NUMERIC_STRING_LIST_RESPONSE, response['payment_ids'])

    def test_parse_direct_resonse(self):
        response_element = E.fromstring(DIRECT_RESPONSE_XML.strip())
        response = parse_response(response_element)
        self.assertEquals(TRANSACTION_RESPONSE, response)

    def test_parse_transaction_list(self):
        response_element = E.fromstring(TRANSACTION_LIST_RESPONSE_XML.strip())
        response = parse_response(response_element)
        self.assertEquals(TRANSACTION_LIST_RESPONSE, response)
