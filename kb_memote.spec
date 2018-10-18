/*
A KBase module: kb_memote
Brief description about memote
*/

module kb_memote {

    /*
        A 'typedef' can also be used to define compound or container
        objects, like lists, maps, and structures.  The standard KBase
        convention is to use structures, as shown here, to define the
        input and output of your function.  Here the input is a
        reference to the Assembly data object, a workspace to save
        output, and a length threshold for filtering.

        To define lists and maps, use a syntax similar to C++ templates
        to indicate the type contained in the list or map.  For example:

            list <string> list_of_strings;
            mapping <string, int> map_of_ints;
    */

    typedef structure {
        string compound_id;
        string compound_name;
    } EachCompound;

    typedef structure {
        string workspace;
        string model_id;
        string media_id;
        string out_model_id;
    } RunMemoteParams;

    typedef structure {
        string model_ref;
    } RunMemoteResults;

    funcdef runMemote(RunMemoteParams params) returns (RunMemoteResults output) authentication required;
};
