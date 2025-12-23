#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE First_TestSuite
#include <boost/test/included/unit_test.hpp>
//#include <boost/test/unit_test.hpp>


#include "src/DataBucket.hpp"
#include "src/DumbModbus.hpp"

BOOST_AUTO_TEST_SUITE(LL_Tests)

#define shiftt 2
BOOST_AUTO_TEST_CASE(Modbusros_test)
{
    dumb_Mserver srv;
    srv.ezTreadstart();

    
    uint16_t out[2] = {55,66};
    DataBucket dd('R',(uint16_t)shiftt,(uint16_t)8);
    DataBucket ddw('W',(uint16_t)2,(uint16_t)2);
    ddw.write(out,2);
    //DataBucket * datta = & dd;

    uint16_t regs[8] = {0,0,3,0,0,0,0,0};
    //uint8_t coils[10];
    ModbusRos comm ;
    comm.addtask(&dd);
    comm.addtask(&ddw);
    //comm.addtask('R',1,8,regs);
    //comm.addtask('R',1,8,regs);
    //comm.addtask('c',1,10,(uint16_t*)coils);
    

    comm.relink("127.0.0.1",1502);
    //comm.addtask('R',1,8,regs);
    std::cout << dd.get_rdy() <<std::endl;
    dd.read(regs);
    
    for (size_t i = 0; i < 8; i++)
    {
        BOOST_CHECK_EQUAL(regs[i],(uint16_t) (i+shiftt)*2);
    }
    
    //comm.addtask('R',1,8,regs);
    
    //BOOST_CHECK_EQUAL(regs[7],(uint16_t) 88);
    //BOOST_CHECK_MESSAGE(regs[6] == 77, "regs rly" << regs[6]);
    
}



BOOST_AUTO_TEST_SUITE_END()