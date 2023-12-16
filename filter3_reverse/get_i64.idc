#include <idc.idc>

static main()
{
	auto_mark_range(0, BADADDR, AU_FINAL);
	msg("Waiting for the end of the auto analysis...\n");
	auto_wait();
	msg("All done, exiting...\n");
	qexit(0); // exit to OS, error code 0 - success
}