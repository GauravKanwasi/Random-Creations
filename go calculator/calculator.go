package main

import (
    "errors"
    "fmt"
    "strconv"
    "strings"
)

func calculate(a float64, op string, b float64) (float64, error) {
    switch op {
    case "+":
        return a + b, nil
    case "-":
        return a - b, nil
    case "*":
        return a * b, nil
    case "/":
        if b == 0 {
            return 0, errors.New("division by zero")
        }
        return a / b, nil
    default:
        return 0, errors.New("invalid operator")
    }
}

func main() {
    fmt.Println("Welcome to the Simple Calculator!")
    fmt.Println("Enter expressions like '2 + 3' (with spaces) or 'exit' to quit.")

    for {
        fmt.Print("Enter expression: ")
        var input string
        fmt.Scanln(&input)
        input = strings.TrimSpace(input)

        if strings.ToLower(input) == "exit" {
            break
        }

        fields := strings.Fields(input)
        if len(fields) != 3 {
            fmt.Println("Invalid input. Please enter an expression like '2 + 3'.")
            continue
        }

        a, err := strconv.ParseFloat(fields[0], 64)
        if err != nil {
            fmt.Println("Invalid number:", fields[0])
            continue
        }

        op := fields[1]

        b, err := strconv.ParseFloat(fields[2], 64)
        if err != nil {
            fmt.Println("Invalid number:", fields[2])
            continue
        }

        result, err := calculate(a, op, b)
        if err != nil {
            fmt.Println("Error:", err)
            continue
        }

        fmt.Printf("%v %s %v = %v\n", a, op, b, result)
    }

    fmt.Println("Goodbye!")
}
