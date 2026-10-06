// Задание 4. Передача данных из Python в Go через JSON (stdin/stdout).
//
// Программа читает один JSON-объект из stdin, выполняет вычисление
// и пишет JSON-ответ в stdout. Ошибки пишутся в stderr, код возврата - 1.
package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
)

type request struct {
	Label   string  `json:"label"`
	Numbers []int64 `json:"numbers"`
}

type response struct {
	Label        string `json:"label,omitempty"`
	Count        int    `json:"count"`
	SumOfSquares int64  `json:"sum_of_squares"`
	Sum          int64  `json:"sum"`
}

// errInvalidPayload возвращается, если во входных данных нечего обрабатывать.
var errInvalidPayload = errors.New(`поле "numbers" должно быть непустым массивом чисел`)

// readRequest читает и разбирает один JSON-объект из входного потока.
func readRequest(r io.Reader) (request, error) {
	var req request

	decoder := json.NewDecoder(r)
	decoder.DisallowUnknownFields()

	if err := decoder.Decode(&req); err != nil {
		return request{}, fmt.Errorf("не удалось разобрать JSON: %w", err)
	}
	if len(req.Numbers) == 0 {
		return request{}, errInvalidPayload
	}

	return req, nil
}

// calculate считает сумму и сумму квадратов переданных чисел.
func calculate(req request) response {
	var sum, sumOfSquares int64
	for _, n := range req.Numbers {
		sum += n
		sumOfSquares += n * n
	}

	return response{
		Label:        req.Label,
		Count:        len(req.Numbers),
		SumOfSquares: sumOfSquares,
		Sum:          sum,
	}
}

func run(stdin io.Reader, stdout io.Writer) error {
	req, err := readRequest(stdin)
	if err != nil {
		return err
	}

	encoder := json.NewEncoder(stdout)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(calculate(req)); err != nil {
		return fmt.Errorf("не удалось записать ответ: %w", err)
	}

	return nil
}

func main() {
	if err := run(os.Stdin, os.Stdout); err != nil {
		fmt.Fprintf(os.Stderr, "ошибка: %v\n", err)
		os.Exit(1)
	}
}
