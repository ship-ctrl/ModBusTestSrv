/// @brief example test

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE Example
#include <boost/test/included/unit_test.hpp>


//#include <iostream>
//#include <cmath>
//#include "header_to_test.hpp"

BOOST_AUTO_TEST_SUITE(ExampleTest)

inline int example() {return 0;}

/// @brief test checking example() is runable
/// @param  casename
BOOST_AUTO_TEST_CASE(nothrowtest)
{
    BOOST_CHECK_EQUAL(example(),0);
}


BOOST_AUTO_TEST_SUITE_END()