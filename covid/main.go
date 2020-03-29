package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"strings"
)

type State struct {
	Id         int
	Name       string
	Population int64
}

func GetData(url string) (string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	b, e := ioutil.ReadAll(resp.Body)
	if e != nil {
		return "", e
	}

	return string(b), nil
}

func getStateData() ([]State, error) {
	b, e := ioutil.ReadFile("states.json")
	if e != nil {
		return nil, e
	}

	states := []State{}
	e = json.Unmarshal(b, &states)
	if e != nil {
		return nil, e
	}

	return states, nil
}

func getColumnIndex(names []string, name string) int {
	for i, w := range names {
		if w == name {
			return i
		}
	}

	return -1
}

func getStateInfo(states []State, id int) State {
	var state State
	for i := range states {
		if states[i].Id == id {
			state = states[i]
			return state
		}
	}

	return State{}
}

func main() {

	states, e := getStateData()
	if e != nil {
		fmt.Println("Error reading state data!!", e)
		os.Exit(1)
	}

	json, _ := json.MarshalIndent(states, "  ", "  ")
	fmt.Println(string(json))

	url := "http://covidtracking.com/api/states.csv"
	data, e := GetData(url)
	if e != nil {
		fmt.Println("Error!!", e)
		os.Exit(1)
	}

	lines := strings.Split(data, "\n")
	headers := strings.Split(lines[0], ",")
	fip := getColumnIndex(headers, "fips")
	pos := getColumnIndex(headers, "positive")
	neg := getColumnIndex(headers, "negative")
	hosp := getColumnIndex(headers, "hospitalized")
	death := getColumnIndex(headers, "death")

	totalLines := len(lines)
	fmt.Println("Id,State,Population,Positive,Negative,Hospitalized,Death")
	for i := 1; i < totalLines; i++ {
		cols := strings.Split(lines[i], ",")

		id, _ := strconv.Atoi(cols[fip])
		if id >= 60 { // skip territories
			continue
		}
		state := getStateInfo(states, id)
		fmt.Printf("%v,%v,%v,%v,%v,%v,%v\n", id, state.Name, state.Population, cols[pos], cols[neg], cols[hosp], cols[death])
	}
}
