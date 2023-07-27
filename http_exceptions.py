from src.utils.common.responses.handlers.exceptions import ErrorHandler
from src.utils.common.aws.aws_ses import send_mail



def exception_handler(module=None, func=None, token_data=None, db=None, request=None):
    try:
        dev_details=ErrorHandler.error_for_developer(exception_url=request.url)
        send_mail(dev_details=dev_details)
        return message
    
    except Exception as e:
        record_audit(f"exception_handler: unhandled exception : {e}")
        return str(e)