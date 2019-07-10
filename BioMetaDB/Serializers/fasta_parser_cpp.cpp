#include <string>
#include <fstream>
#include <iostream>
#include "fasta_parser_cpp.h"

/*
Class will parse fasta and return vector string arrays, indices are fasta id,
remaining header values, and fasta record

*/

namespace fasta_parser {
    FastaParser_cpp::FastaParser_cpp() {}

    FastaParser_cpp::FastaParser_cpp(std::ifstream& f, std::string delim = " ",
                std::string head = ">") {
        fastaFile = &f;
        delimiter = delim;
        header = head;
        last_line = "";
    }

    FastaParser_cpp::~FastaParser_cpp() {}

    void FastaParser_cpp::grab(std::vector<std::string>& line_data) {
        std::string line;
        std::string dataLine;
        if (line_data.size() > 0) {
            line_data.clear();
        }
        size_t pos = 0;
        if (!(*this->fastaFile).eof()) {
            if (this->last_line != "") {
                line = this->last_line;
            }
            while (line.compare(0, this->header.length(), this->header) != 0 && !(*this->fastaFile).eof()) {
                getline((*this->fastaFile), line);
            }
            pos = line.find(this->delimiter);
            if (pos == 0) {
                line_data.push_back(line.substr(1));
                line_data.push_back("");
            } else {
                line_data.push_back(line.substr(1, pos - 1));
                line_data.push_back(line.substr(pos + 1, line.length()));
            }
            getline((*this->fastaFile), line);
            while (line.compare(0, this->header.length(), this->header) != 0 && !(*this->fastaFile).eof()) {
                dataLine.append(line);
                getline((*this->fastaFile), line);
            }
            line_data.push_back(dataLine);
            this->last_line = line;
        }
    }

}
