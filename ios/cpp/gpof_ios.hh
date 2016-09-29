#pragma once

#include <regex>
#include <iod/foreach.hh>
#include <boost/lexical_cast.hpp>

namespace gpof
{
  inline
  std::map<std::string, std::string> read_parameters(std::string filename)
  {
    std::ifstream f(filename);

    std::map<std::string, std::string> map;

    int line_id = 1;
    while (f.good())
    {
      std::string line;
      std::getline(f, line);

      if (line.size() == 0) continue;
      std::regex e ("\\s*([^:\\s]*)\\s*:\\s*([^\\s]*)\\s*");
      std::smatch m;

      if (std::regex_search(line,m,e))
      {
        std::cout << m[1] << ':' << m[2] << std::endl;
        map[m[1]] = m[2];
      }
      else
        std::cerr << "Configuration file error at " << filename << ":" << line_id << " " << line << std::endl;
    
      line_id++;    
    }

    f.close();
    return map;
  }

  template <typename... T>
  inline void read_parameters(std::string f, T&&... values)
  {
    auto cfg = iod::D(values...);
    auto map = read_configuration(f);

    iod::foreach(cfg) | [&] (auto& p)
    {
      auto it = map.find(p.symbol().name());
      if (it != map.end())
      {
        try
        {
          p.value() = boost::lexical_cast<std::remove_reference_t<decltype(p.value())>>(it->second);
        }
        catch (...)
        {
          throw std::runtime_error(std::string("Could not parse value of parameter ") + p.symbol().name());
        }
      }
    };
  }

  template <typename... T>
  inline void write_results(std::string f, T&&... values)
  {
    auto results = iod::D(values...);

    std::ofstream file(f);
    
    iod::foreach(results) | [&] (auto p)
    {
      file << p.symbol_name() << ": " << p.value() << std::endl; 
    };

  }
  
}
