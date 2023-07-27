from src.config.data import params
from src.utils.common.utils import get_env_name
from src.utils.common.constants import CHARSET
from src.utils.common.record_audits import record_audit
from src.utils.common.responses.handlers.exceptions import ErrorHandler
import boto3


def get_mailer_body(dev_details=None):
    try:
        api_url, api_file, api_detail, api_line, trace_flow = dev_details.get("api_url"), dev_details.get("api_exception_file"), dev_details.get("api_exception_detail"),  dev_details.get("api_exception_line_no"), dev_details.get("trace_flow")
        type_, object_, file_, line, detail  = dev_details.get("exception_type"), dev_details.get("exception_object"), dev_details.get("exception_file"),  dev_details.get("exception_line"), dev_details.get("exception_detail")
        nxt = '\n'
        
        content =  "{nxt} ---------------Developer Details --------------- {nxt}\
                    {nxt} API URL: {api_url}\
                    {nxt} Error File.: {file_}\
                    {nxt} Error Line No.: {line}\
                    {nxt} Error Detail: {detail}\
                    {nxt} Error Type: {type_}\
                    {nxt} Error Object: {object_}\
                    {nxt} API File: {api_file}\
                    {nxt} API Error Detail: {api_detail}\
                    {nxt} API Error Line No.: {api_line}\
                    {nxt} {nxt} Trace Flow: {trace_flow}"\
                        .format(nxt=nxt,type_=type_, object_=object_, file_=file_, line=line, detail=detail, 
                                api_url=api_url, api_file=api_file, api_detail=api_detail, api_line=api_line, trace_flow=trace_flow )
        return content
    
    except Exception as e:
        dev_details = ErrorHandler.error_for_developer()
        record_audit(f"get_mailer_body: unhandled exception : error : {dev_details}")
        raise e

def send_mail(sender="noreply@sample.com", recipients=["recipent_mail@sample.com", "another_one@sample.com"], subject=None, dev_details=None,  cc=[], bcc=[], content_type= "text"):
    try:
        if subject is  None:
            subject = "Issue Tracker Mail"

        env = get_env_name().lower()
        if env in ['dev', 'beta', 'prod']:
            content = get_mailer_body(dev_details=dev_details)
            subject_ = f"[{env} server] : {subject}"
            msg_body = AWSSendEmailService.get_message_body_by_format(subject=subject_, content=content, format=content_type)
            response = AWSSendEmailService.aws_send_mail(sender=sender, recipients=recipients, subject=subject, content=msg_body, cc=cc, bcc=bcc, content_type=content_type)
            return response
    
    except Exception as e:
        dev_details = ErrorHandler.error_for_developer()
        record_audit(f"send_mail: unhandled exception : error : {dev_details}")
        raise e

class AWSSendEmailService:
    @staticmethod
    def aws_send_mail(sender="", recipients=[], subject="", content="", cc=[], bcc=[], content_type="text"):
        try:
            AWS_REGION = params.get('AWSRegionSES')
            AWS_REGION_SES = params.get('AWSRegionSES')
            client = boto3.client(AWS_REGION_SES, region_name=AWS_REGION)
            destination = {
                'ToAddresses': recipients
            }
            if cc:
                if isinstance(cc, str):
                    destination.update({'CcAddresses': [cc]})
                else:
                    destination.update({'CcAddresses': cc})
            if bcc:
                if isinstance(bcc, str):
                    destination.update({'BccAddresses': [bcc]})
                else:
                    destination.update({'BccAddresses': bcc})
                
            response = client.send_email(
                    Destination=destination,
                    Message=AWSSendEmailService.get_message_body_by_format(subject, content=content, format=content_type),
                    Source=sender
                )
            return response
        except Exception as e:
            dev_details = ErrorHandler.error_for_developer()
            record_audit(f"aws_send_mail: unhandled exception : error : {dev_details}")
            raise e


    @staticmethod
    def get_message_body_by_format(subject=None, content=None, format='text'):
        try:
            message_body = {
                'Subject': {
                        'Charset': CHARSET,
                        'Data': subject,
                    }
                }
            if format.lower() == "text":
                message_body.update({
                    'Body': {
                        'Text': {
                            'Charset': CHARSET,
                            'Data': content,
                        }
                    }
                })
            elif format.lower() == "html":
                message_body.update({
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': content,
                        }
                    }
                })
            return message_body
        
        except Exception as e:
            dev_details = ErrorHandler.error_for_developer()
            record_audit(f"get_message_body_by_format: unhandled exception : error : {dev_details}")
            raise e
