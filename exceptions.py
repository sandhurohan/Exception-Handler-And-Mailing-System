from src.utils.common.record_audits import record_audit
from src.utils.common.constants import MICROSERVICE, ENV
from pprint import pprint
import linecache
import sys
import traceback


class ErrorHandler:
    @staticmethod
    def get_errors_in_detail(tb=None):
        try:
            trace_detail, trace_list = traceback.extract_tb(tb=tb), []
            error = {}
            for trace in trace_detail:
                file_name = str(trace.filename)
                if (ENV not in file_name) and (MICROSERVICE in file_name):
                    trace = [trace, trace.line]
                    trace_list.append(trace)
            
            if trace_list:
                last_trace = trace_list[-1][0]
                error = { "file" : last_trace.filename, "line": last_trace.lineno, "detail": last_trace.line}
            
            traceback_details = {"trace_flow": trace_list, "error": error}
            record_audit(f"get_errors_in_detail: traceback_details: {traceback_details}")
            return traceback_details

        except Exception as e:
            record_audit(f"error_for_developer: unhandled exception: {e}")
            return str(e)
    
    @staticmethod
    def error_for_developer(exception_url=None):
        """ Returns Dict according to Exception Occured.
            sys.exc_info function returns a 3-tuple with the exception, the exception's parameter, and a traceback object that pinpoints the line of Python that raised the exception.
            linecache.getline() returns particular line by providing a line number, filename etc.
        """
        try:
            exc_type, exc_obj, tb = sys.exc_info() 
            f = tb.tb_frame
            start_lineno, start_filename = tb.tb_lineno, f.f_code.co_filename
            linecache.checkcache(start_filename)
            line = linecache.getline(start_filename, start_lineno, f.f_globals) 
            end_lineno, end_filename, end_detail =  start_lineno, start_filename, line
            
            trace_details = ErrorHandler.get_errors_in_detail(tb=tb)
            record_audit(f"error_for_developer: trace_details: {trace_details} ")
            trace_flow =  trace_details.get("trace_flow")
            
            if trace_flow:
                end_lineno, end_filename, end_detail =  trace_details.get("error").get("line"), trace_details.get("error").get("file"), trace_details.get("error").get("detail")

            dev_details = { 
                'api_url': str(exception_url), 
                'exception_file': str(end_filename), 
                'exception_line': str(end_lineno), 
                'exception_detail' : str(end_detail), 
                'exception_type': str(exc_type), 
                'exception_object': str(exc_obj) ,
                'api_exception_file': str(start_filename),
                'api_exception_detail': str(line),
                'api_exception_line_no': str(start_lineno),
                'trace_flow': trace_flow
            }
            record_audit(f"error_for_developer: dev_details: {dev_details} ")
            pprint(dev_details, indent=3)          
            return dev_details
        
        except Exception as e:
            record_audit(f"error_for_developer: unhandled exception: {e}")
            return str(e)