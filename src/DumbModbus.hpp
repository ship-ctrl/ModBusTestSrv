#pragma once

#include "modbus/modbus.h"

#include <unistd.h>
#include <stdexcept>
#include <iostream>
#include <string>
#include <atomic>
#include <thread>

class dumb_Mserver
{
private:

    int ro_bits = 20;
    int coil = 20;
    int ro_regs = 20;
    int rw_regs = 20;
    int nb_masters = 1;

    std::atomic<bool> running;
    pthread_t thread = 0;
    std::thread server;

    modbus_t *context = nullptr;
    modbus_mapping_t *mb_mapping = nullptr;
    int port = 1502;
    int soc = -1;
    int rc;
    std::string ip = "127.0.0.1";

    /// @brief initializes context, locks port (creates socket)
    /// @return true on sucsess
    inline bool make_context() {context = modbus_new_tcp(ip.c_str(), port); if(context == nullptr){throw std::ios_base::failure("Failed to create the Modbus context!"); return false;} return true;}
    
    /// @brief initializes memory map to store registers 20 of each by default (or set sizes first)
    /// @return true on sucsess
    inline bool make_map() {mb_mapping = modbus_mapping_new(ro_bits,coil,ro_regs,rw_regs); if (mb_mapping == nullptr){throw std::overflow_error(std::string("mem fuckup")); return false;} return true;}

    /// @brief at the edge of the rainbow, where eagles learn to fly All modbus dreams becomes so clear
    /// @return true on sucsess
    inline bool make_listen() 
    {
        soc = modbus_tcp_listen(context, nb_masters); 
        if (soc == -1) 
        {
            modbus_free(context);
            throw std::ios_base::failure("soc creation FAILED");
            return false;
        }
        return true;
    }

    /// @brief spawns data into registers, reading 0's is boring
    /// @return pointer to Flint's treashure 
    bool spawn_values()
    {
        for (size_t i = 0; i < mb_mapping->nb_bits; i++)
        {
            mb_mapping->tab_bits[i] = i%3%2; //100100
        }
        for (size_t i = 0; i < mb_mapping->nb_input_bits; i++)
        {
            mb_mapping->tab_input_bits[i] = i%2;//1010
        }
        for (size_t i = 0; i < mb_mapping->nb_input_registers; i++)
        {
            mb_mapping->tab_input_registers[i] = i*2;
        }
        for (size_t i = 0; i < mb_mapping->nb_registers; i++)
        {
            mb_mapping->tab_registers[i] = i*3;
        }

        return true;
    }

public:

    /// @brief uses modbus_mapping_new()
    /// @param rob bits
    /// @param rwb input bits
    /// @param rod registers
    /// @param rwd input registers
    /// @throws std::overflow_error() on bad mem mgmt
    /// @return true on sucsess 
    inline bool setRegSizes(const int &rob,const int &rwb,const int &rod,const int &rwd) 
    {
        ro_bits = rob; coil = rwb; ro_regs = rod; rw_regs = rwd; 
        return make_map(); // not war
    }

    /// @brief 
    /// @param nip new IP it's yours (exist cos u can have multiple ones u dummy, on different physycal/virtual devices)
    /// @param listen_port port u wanna listen to
    /// @throws rethrows context/soc error
    /// @return 
    inline bool set_context(const std::string & nip, const int & listen_port)
    {
        ip = nip;
        port = listen_port;
        return make_context();
    }

    /// @brief don't think RUN
    void ezRun()
    {
        make_map();
        spawn_values();
        make_context();
        make_listen();
        soc = modbus_tcp_accept(context, &soc);
        running = true;

        while (running)
        {
            uint8_t query[MODBUS_TCP_MAX_ADU_LENGTH];
            rc = modbus_receive(context, query);
            if (rc > 0) 
            {
                /* rc is the query size */
                modbus_reply(context, query, rc, mb_mapping);
                
                if (mb_mapping->tab_input_registers[6] == 6*5)
                {
                    mb_mapping->tab_input_registers[6] = 12;
                }
                else if (mb_mapping->tab_input_registers[6] == 12)
                {
                    mb_mapping->tab_input_registers[6] = 6*5;
                }
                
            } 
            else if (rc == -1) 
            {
                /* Connection closed by the client or error */
                close(soc);
                running = false;
            }
        }
    }

    /// @brief treading stuff or smth
    inline void ezTreadstart()
    {
        running = true;
        server = std::thread(&dumb_Mserver::ezRun, this);
    }

    /// @brief Wanna join?
    inline void stop() 
    {
        running = false;
        if (server.joinable()) {
            server.join();
        }
    }

    /// @brief paterns are(100100,1010,2468,36912)
    /// @param rob ro_bits
    /// @param rwb coil
    /// @param rod ro_regs
    /// @param rwd rw_regs
    /// @return T on suc
    bool spawn_values(const int &rob,const int &rwb,const int &rod,const int &rwd)
    {
        if ((ro_bits != rob) && (coil != rwb) && (ro_regs != rod) && (rw_regs != rwd))
        {
            setRegSizes(rob,rwb,rod,rwd);
        }
        for (size_t i = 0; i < mb_mapping->nb_bits; i++)
        {
            mb_mapping->tab_bits[i] = i%3%2; //100100
        }
        for (size_t i = 0; i < mb_mapping->nb_input_bits; i++)
        {
            mb_mapping->tab_input_bits[i] = i%2;//1010
        }
        for (size_t i = 0; i < mb_mapping->nb_input_registers; i++)
        {
            mb_mapping->tab_input_registers[i] = i*2;
        }
        for (size_t i = 0; i < mb_mapping->nb_registers; i++)
        {
            mb_mapping->tab_registers[i] = i*3;
        }
        std::cerr << "spawned" << std::endl;
        return true;
        
    }

    /// @brief why couldn't it be class ModBus {} = defalut? :((((
    dumb_Mserver() = default;

    /// @brief bring up chaos and DESTRUCTION uppon those whimpy server objects
    ~dumb_Mserver() {stop(); if (soc != -1){close(soc);close(port);} modbus_mapping_free(mb_mapping); modbus_close(context); modbus_free(context);};

    /// @brief rudimentary @todo modify to a funny trap by adding @throw feathureNotImplemented
    void run();
};