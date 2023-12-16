# include <idc.idc>

static main() {
    Batch(0);
    Wait();
    Exit( 1 - RunPlugin("binexport12_ida64", 2));
}