#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <stack>
#include <map>
#include "pin.H"

FILE * ftrace;
FILE * btrace;
static UINT64 icount = 0;
static UINT64 ibcount = 0;
std::vector <string> modules;
std::map <unsigned long int, pair<std::string, std::string> > values;
std::map <unsigned long int, unsigned long int> translate;
std::map <unsigned long int, bool> hits;
#define True TRUE
#define False FALSE
#define SIZE_CALL 5
#define TRIM_MODE 1
std::string simg;

VOID docount() {
	icount++;
	ibcount++;
}

VOID rtncount(ADDRINT address) {
	if(hits.find(address) == hits.end()) {
                hits.insert(make_pair(address, True));
        }
	fprintf(ftrace, "<%ld, i, #%ld>\n", address, icount);
        icount = 0;
        fflush(ftrace);
	return;
}

VOID rtnretcount(ADDRINT address) {
	fprintf(ftrace, "<%ld, e, #%ld>\n", address, icount);
        icount = 0;
        fflush(ftrace);
	return;
}


bool IsAddressInModule(ADDRINT addr) {
        IMG img = IMG_FindByAddress(addr);
        string path = (IMG_Valid(img) ? IMG_Name(img) : "InvalidImg");
        std::vector <string>::iterator it;
        it = std::find(modules.begin(), modules.end(), path);
        if (it != modules.end())
                return True;
        else
            return False;
}

VOID Image(IMG Img, VOID *v) {
        if(!IMG_IsMainExecutable(Img)) 
                modules.push_back(IMG_Name(Img).c_str());
	return;
}

VOID handle_branch(ADDRINT target, BOOL taken, ADDRINT pc) {
	if(!taken)
		return;

	fprintf(btrace, "<%ld, #%ld>\n", pc, ibcount);
	fflush(btrace);
	ibcount = 0;

}

const char * StripPath(const char * path) {
    const char * file = strrchr(path,'/');
    if (file)
        return file+1;
    else
        return path;
}


VOID Instruction(INS ins, VOID *v) {

	if(TRIM_MODE) {
		if(IsAddressInModule(INS_Address(ins)))
                	 return;
	}

	if(INS_IsBranch(ins)) {
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)handle_branch, IARG_BRANCH_TARGET_ADDR, IARG_BRANCH_TAKEN, IARG_INST_PTR, IARG_END);
	}

	else
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_END);
	return;
}

VOID Routine(RTN rtn, VOID *v) {
	std::string _name = RTN_Name(rtn);
	ADDRINT _address = RTN_Address(rtn);
	std::string _image = StripPath(IMG_Name(SEC_Img(RTN_Sec(rtn))).c_str());
	
	if(TRIM_MODE) {
		if(_image == simg);
		else
			return;
	}

	std::vector <string>::iterator it;
        it = std::find(modules.begin(), modules.end(), _image);
        if (it != modules.end())
                return;

	if(values.find(_address) == values.end()) {
		values.insert(make_pair(_address, make_pair(_name, _image)));
	}

	RTN_Open(rtn);
	RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)rtncount, IARG_PTR, _address, IARG_END);

	RTN_InsertCall(rtn, IPOINT_AFTER, (AFUNPTR)rtnretcount, IARG_PTR, _address, IARG_END);

	RTN_Close(rtn);
	return;
}

KNOB<string> KnobFFile(KNOB_MODE_WRITEONCE, "pintool",
	"o", "func.out", "specify output func file name");

KNOB<string> KnobBFile(KNOB_MODE_WRITEONCE, "pintool",
	"p", "branch.out", "specify output branch file name");

VOID Fini(INT32 code, VOID *v) {
	for(unsigned int ii = 0; ii < modules.size(); ii++)
		cout << modules[ii] << endl;
	FILE * naming;
	std::string fname = simg + "_names.out";
	naming = fopen(fname.c_str(), "w");
	std::map< unsigned long int, pair<std::string, std::string> > :: iterator it;

	fprintf(naming, "ID\tFunction_ID\n");
	fflush(naming);
	for(it = values.begin(); it != values.end(); it++) {
		if(hits[it->first] == True)
			fprintf(naming, "%ld\t%s\n", it->first, (it->second).first.c_str());
	}
	fflush(naming);
	fclose(naming);
	return;
}

/* ===================================================================== */
/* Print Help Message													 */
/* ===================================================================== */

INT32 Usage()
{
	cerr << "This tool counts the number of dynamic instructions executed" << endl;
	cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
	return -1;
}

/* ===================================================================== */
/* Main																	 */
/* ===================================================================== */
/*	 argc, argv are the entire command line: pin -t <toolname> -- ...	 */
/* ===================================================================== */

int main(int argc, char * argv[])
{
	// Initialize pin
	if (PIN_Init(argc, argv)) return Usage();

	std::string s(argv[10]);
	std::string delimiter = "/";
	size_t pos = 0;
	std::string token;
	while ((pos = s.find(delimiter)) != std::string::npos) {
		token = s.substr(0, pos);
		s.erase(0, pos + delimiter.length());
	}
	simg = s;
	PIN_InitSymbols();

	std::string fname = simg  + "_func_" + KnobFFile.Value().c_str();
	std::string bname = simg + "_branch_" + KnobBFile.Value().c_str();

	ftrace = fopen(fname.c_str(), "w");
	btrace = fopen(bname.c_str(), "w");

	INS_AddInstrumentFunction(Instruction, 0);
	IMG_AddInstrumentFunction(Image, 0);
	RTN_AddInstrumentFunction(Routine, 0);

	// Register Fini to be called when the application exits
	PIN_AddFiniFunction(Fini, 0);
	
	// Start the program, never returns
	PIN_StartProgram();
	
	fclose(ftrace);
	fclose(btrace);
	return 0;
}
