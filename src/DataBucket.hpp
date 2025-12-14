#pragma once

#include <queue>
#include <mutex>
#include <atomic>
#include <condition_variable>

/// @attention in fact all this class is usles and should be wiped out to finaly be replased by std::tuple<char,uint,uint>
/// @brief stores std::atomic<uint16_t> in dequeue (nearest vector analogue 4 copy/move haters)
class DataBucket
{
private:
    
    /// @brief deprecated
    std::deque<std::atomic<uint16_t>> data;

    /// @brief going to deprecate
    std::atomic_bool rdy;
    DataBucket(DataBucket &) = delete;

public:
    char opCode;
    uint16_t startReg, qty;
    std::mutex _data_mutex;
    std::condition_variable _task_pending;
    
    
    /// @brief cumstructor or smth
    /// @param code operation code
    /// @param start startReg
    /// @param num numregs
    DataBucket(const char& code, const uint16_t& start, const uint16_t& num) {opCode = code; startReg = start; qty = num;} 
    ~DataBucket() = default;
    
    inline void set_rdy(bool set) {rdy = set;}
    inline bool get_rdy() {return (rdy == true);}
    inline int size() {return data.size();}

    /// @brief sycronized read
    /// @param out where to read ptr
    /// @return true on sssssss
    inline bool read(uint16_t * out) 
    {
        int c = 0;
        std::unique_lock<std::mutex> lk(_data_mutex);
        _task_pending.wait(lk,[this]{return &rdy;});
        for (auto &&i : data)
        {
            out[c] = i;
            c++;
        }
        lk.unlock();
        rdy = false;
        return true;
    }
    
    /// @brief read as mutex allows
    /// @param out where to read ptr
    /// @return true on true
    inline bool read_tread(uint16_t * out) 
    {
        int c = 0;
        std::lock_guard<std::mutex> lk(_data_mutex);
        
        for (auto &&i : data)
        {
            out[c] = i;
            c++;
        }
        
        return true;
    }

    /// @brief writes into bucket of atomic (differs length before)
    /// @param inp looks like u want to write smth (ptr)
    /// @param length HOW MUCH WOULD IT STILL?
    /// @return true on pretty cats birthdays
    inline bool write(uint16_t * inp, const uint16_t & length) 
    {   
        qty = length;
        std::lock_guard<std::mutex> lk(_data_mutex);
        for (size_t i = 0; i < qty; i++)
        {
            data.emplace_back(inp[i]);
        }
        
        return true;
    }

    /// @brief same write but once length is constant
    /// @param inp write smth on a little peace of paper, give a compiller pointer to it
    /// @return ftrue onf fevery runf
    inline bool write(uint16_t * inp) 
    {   
        std::lock_guard<std::mutex> lk(_data_mutex);
        for (size_t i = 0; i < qty; i++)
        {
            data.emplace_back(inp[i]);
        }
        
        return true;
    }

};