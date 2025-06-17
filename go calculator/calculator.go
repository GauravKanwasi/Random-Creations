package main

import (
    "errors"
    "fmt"
    "strings"
    "github.com/Knetic/govaluate"
    "math"
)

// Define custom mathematical functions
var functions = map[string]govaluate.ExpressionFunction{
    "sin": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("sin expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("sin argument must be a number")
        }
        return math.Sin(val), nil
    },
    "cos": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("cos expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("cos argument must be a number")
        }
        return math.Cos(val), nil
    },
    "tan": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("tan expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("tan argument must be a number")
        }
        return math.Tan(val), nil
    },
    "sind": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("sind expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("sind argument must be a number")
        }
        rad := val * math.Pi / 180
        return math.Sin(rad), nil
    },
    "cosd": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("cosd expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("cosd argument must be a number")
        }
        rad := val * math.Pi / 180
        return math.Cos(rad), nil
    },
    "tand": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("tand expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("tand argument must be a number")
        }
        rad := val * math.Pi / 180
        return math.Tan(rad), nil
    },
    "sqrt": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("sqrt expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("sqrt argument must be a number")
        }
        if val < 0 {
            return nil, errors.New("sqrt of negative number")
        }
        return math.Sqrt(val), nil
    },
    "log": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("log expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("log argument must be a number")
        }
        if val <= 0 {
            return nil, errors.New("log of non-positive number")
        }
        return math.Log(val), nil
    },
    "exp": func(args ...interface{}) (interface{}, error) {
        if len(args) != 1 {
            return nil, errors.New("exp expects one argument")
        }
        val, ok := args[0].(float64)
        if !ok {
            return nil, errors.New("exp argument must be a number")
        }
        return math.Exp(val), nil
    },
}

// Define constants
var parameters = map[string]interface{}{
    "pi": math.Pi,
    "e":  math.E,
}

func main() {
    fmt.Println("Welcome to the Enhanced Calculator!")
    fmt.Println("Enter mathematical expressions like '2 + 3', 'sin(30)', or 'sind(45)'.")
    fmt.Println("Supported functions: sin, cos, tan (radians), sind, cosd, tand (degrees), sqrt, log, exp")
    fmt.Println("Constants: pi, e")
    fmt.Println("Type 'exit' to quit.")

    for {
        fmt.Print("Enter expression: ")
        var input string
        fmt.Scanln(&input)
        input = strings.TrimSpace(input)

        if strings.ToLower(input) == "exit" {
            break
        }

        evaluator, err := govaluate.NewEvaluableExpressionWithFunctions(input, functions)
        if err != nil {
            fmt.Println("Invalid expression:", err)
            continue
        }

        result, err := evaluator.Evaluate(parameters)
        if err != nil {
            fmt.Println("Error evaluating expression:", err)
            continue
        }

        if res, ok := result.(float64); ok {
            fmt.Printf("Result: %v\n", res)
        } else {
            fmt.Println("Result is not a number")
        }
    }

    fmt.Println("Goodbye!")
}
