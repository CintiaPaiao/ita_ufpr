class PAEError(Exception): pass
class SchemaError(PAEError): pass
class DataQualityError(PAEError): pass
class MissingParameterError(PAEError): pass
class IntegrationError(PAEError): pass
class AuthorizationError(PAEError): pass
class WorkflowError(PAEError): pass
