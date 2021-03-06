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

	url := "http://covidtracking.com/api/states.csv"
	data, e := GetData(url)
	if e != nil {
		fmt.Println("Error!!", e)
		os.Exit(1)
	}

	lines := strings.Split(data, "\n")
	headers := strings.Split(lines[0], ",")
	fip := getColumnIndex(headers, "fips")
	posc := getColumnIndex(headers, "positive")
	negc := getColumnIndex(headers, "negative")
	hospc := getColumnIndex(headers, "hospitalized")
	deathc := getColumnIndex(headers, "death")

	totalLines := len(lines)
	fmt.Println("State,Population,Positive,Negative,Hospitalized,Death,DeathPerMill,PosPerMill,DeathPerCent")
	for i := 1; i < totalLines; i++ {
		cols := strings.Split(lines[i], ",")

		id, _ := strconv.Atoi(cols[fip])
		if id >= 60 { // skip territories
			continue
		}
		state := getStateInfo(states, id)

		pos, _ := strconv.ParseInt(cols[posc], 10, 64)
		posPerMill := (float64(pos) / float64(state.Population)) * 1000000

		death, _ := strconv.ParseInt(cols[deathc], 10, 64)
		deathPerMill := (float64(death) / float64(state.Population)) * 1000000

		deathPerCent := (float64(death) / float64(pos)) * 100

		fmt.Printf("%v,%v,%v,%v,%v,%v,%.2f,%.2f,%.2f\n", state.Name, state.Population, cols[posc],
			cols[negc], cols[hospc], cols[deathc], deathPerMill, posPerMill, deathPerCent)
	}
}
