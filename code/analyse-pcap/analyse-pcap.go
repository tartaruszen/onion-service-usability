// Copyright 2017 Philipp Winter <phw@nymity.ch>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

package main

import (
	"flag"
	"fmt"
	"log"
	"strings"

	pcap "github.com/akrennmair/gopcap"
	dns "github.com/miekg/dns"
)

const (
	// 14 (Ethernet) + 20 (IP) + 8 (UDP) = 42
	HEADER_OFFSET = 42
	TIME_LAYOUT   = "2006-01-02.15:04:05"
)

func is_onion_domain(name string, counter int) bool {

	labels := strings.Split(name, ".")
	if len(labels) == 0 {
		return false
	}

	for i := len(labels) - 1; i > 0; i-- {
		if labels[i] == "" {
			continue
		}
		return labels[i] == "onion"
	}

	return false
}

func analysePcap(filename string) {

	handle, err := pcap.Openoffline(filename)
	if err != nil {
		log.Fatal(err)
	}

	counter := 1
	req := new(dns.Msg)

	for pkt := handle.Next(); pkt != nil; counter, pkt = counter+1, handle.Next() {

		if err := req.Unpack(pkt.Data[HEADER_OFFSET:]); err != nil {
			log.Printf("Packet #%d: %s\n", counter, err)
			continue
		}

		for i := 0; i < len(req.Question); i++ {
			if is_onion_domain(req.Question[i].Name, counter) {
				fmt.Printf("%s,%s\n", pkt.Time.Format(TIME_LAYOUT), req.Question[i].Name)
			}
		}
	}
}

func main() {

	pcapFile := flag.String("pcap", "", "Pcap file to analyse.")
	flag.Parse()

	if *pcapFile == "" {
		log.Fatal("No pcap file given.  Use the -pcap argument.")
	}
	analysePcap(*pcapFile)
}
