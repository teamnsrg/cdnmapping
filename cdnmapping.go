package main

import (
	"bufio"
	"encoding/csv"
	log "github.com/sirupsen/logrus"
	"github.com/yl2chen/cidranger"
	"io"
	"io/ioutil"
	"net"
	"os"
	"path"
	"strings"
)

func main() {
	ranges, err := buildTries("cdn_ip")
	if err != nil {
		log.Error("Failed to build CDN tries")
		log.Fatal(err)
	}

	log.Infof("Built tries for %d CDNs", len(ranges))

	if len(os.Args) != 3 {
		log.Error("Usage: ./cdnmapping <path-to-input-file> <path-to-output-file")
	}


	f, err := os.Open(os.Args[1])
	if err != nil {
		log.Error(err)
		return
	}

	g, err := os.Create(os.Args[2])
	if err != nil {
		log.Error(err)
		return
	}

	writer := csv.NewWriter(g)
	reader := csv.NewReader(f)

	lineNum := 0
	for {
		lineNum += 1
		parts, err := reader.Read()
		if err == io.EOF {
			break
		} else if err != nil {
			log.Error(err)
			break
		}

		if len(parts) < 2 {
			log.Warnf("Bad Line: %d", lineNum)
			continue
		}

		domain := parts[0]
		ipString := parts[1]

		ip := net.ParseIP(ipString)
		if ip == nil {
			log.Errorf("Bad line: %d", lineNum)
			continue
		}

		usedCDN := "unknown"
		for cdn, networks := range ranges {
			does, err := (*networks).Contains(ip)
			if err != nil {
				log.Error(err)
				continue
			}
			if does {
				usedCDN = cdn
				break
			}
		}

		err = writer.Write([]string{domain, ipString, usedCDN})
		if err != nil {
			log.Error(err)
		}
	}

}


func buildTries(pathToTries string) (map[string]*cidranger.Ranger, error) {

	IP_ADDR_FILE := "advertised.lst"

	ranges := make(map[string]*cidranger.Ranger)

	dirs, err := ioutil.ReadDir(pathToTries)
	if err != nil {
		return nil, err
	}

	for _, d := range dirs {
		t, err := buildTrie(path.Join(pathToTries, d.Name(), IP_ADDR_FILE))
		if err != nil {
			log.Error(err)
			continue
		}

		ranges[d.Name()] = t
	}

	return ranges, nil
}


func buildTrie(pathToFile string) (*cidranger.Ranger, error) {
	t := cidranger.NewPCTrieRanger()

	f, err := os.Open(pathToFile)
	if err != nil {
		return nil, err
	}

	reader := bufio.NewReader(f)

	for {
		line, _, err := reader.ReadLine()
		if err == io.EOF {
			break
		} else if err != nil {
			return nil, err
		}

		if strings.TrimSpace(string(line)) == "" {
			continue
		}

		_, network, err := net.ParseCIDR(string(line))
		if err != nil {
			log.Error(err)
			continue
		}

		err = t.Insert(cidranger.NewBasicRangerEntry(*network))
		if err != nil {
			log.Error(err)
		}
	}

	return &t, nil
}