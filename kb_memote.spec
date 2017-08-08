/*
A KBase module: kb_memote
Brief description about memote
*/

module kb_memote {
    /*
        A 'typedef' allows you to provide a more specific name for
        a type.  Built-in primitive types include 'string', 'int',
        'float'.  Here we define a type named assembly_ref to indicate
        a string that should be set to a KBase ID reference to an
        Assembly data object.
    */


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


    /*
        Here is the definition of the output of the function.  The output
        can be used by other SDK modules which call your code, or the output
        visualizations in the Narrative.  'report_name' and 'report_ref' are
        special output fields- if defined, the Narrative can automatically
        render your Report.
    */
    /*
        A string representing a model id.
    */

    typedef string model_id;

    /*
        A string representing a workspace name.
    */

    typedef string workspace_name;

    typedef structure {
        string compound_id;
        string compound_name;
    }EachCompound;

    typedef structure {
        workspace_name workspace;
        model_id model_id;
        model_id out_model_id;
        list <EachCompound> compounds;
    } RunMemote;

    typedef structure {
        string model_ref;
    }MemoteResults;

    /*
        The actual function is declared using 'funcdef' to specify the name
        and input/return arguments to the function.  For all typical KBase
        Apps that run in the Narrative, your function should have the
        'authentication required' modifier.
    */

    funcdef runMemote(RunMemote params) returns (MemoteResults output) authentication required;
};
