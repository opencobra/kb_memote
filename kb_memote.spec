/*
A KBase module: kb_memote
*/

module kb_memote {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    typedef structure {
        string workspace;
        string model_id;
        string media_id;
    } RunMemoteParams;
    
    typedef structure {
        string report_name;
        string report_ref;
    } RunMemoteResults;
    
    funcdef run_memote(RunMemoteParams params) returns (RunMemoteResults output) authentication required;
    
    funcdef run_kb_memote(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
