// Задание 2. HTTP-сервер на Go с горутиной для фоновой обработки запросов.
//
// Эндпоинт POST /process принимает JSON, сразу отвечает клиенту,
// а обработка (сумма квадратов) выполняется в отдельной горутине.
// GET /stats показывает, сколько задач уже обработано в фоне.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os/signal"
	"sync"
	"sync/atomic"
	"time"
)

type processRequest struct {
	Numbers []int64 `json:"numbers"`
}

type processResponse struct {
	Status   string `json:"status"`
	JobID    int64  `json:"job_id"`
	Accepted int    `json:"accepted"`
}

type statsResponse struct {
	ProcessedJobs int64 `json:"processed_jobs"`
	LastJobID     int64 `json:"last_job_id"`
	LastSum       int64 `json:"last_sum"`
}

// backgroundProcessor считает задачи в фоновых горутинах и хранит
// результат последней завершённой задачи.
type backgroundProcessor struct {
	// WaitGroup позволяет дождаться завершения фоновых горутин при остановке.
	wg sync.WaitGroup

	nextID    atomic.Int64
	processed atomic.Int64

	mu        sync.Mutex
	lastJobID int64
	lastSum   int64
}

// submit передаёт задачу в фоновую горутину и сразу возвращает её идентификатор.
func (p *backgroundProcessor) submit(numbers []int64) int64 {
	jobID := p.nextID.Add(1)

	p.wg.Add(1)
	go func() {
		defer p.wg.Done()

		sum := sumOfSquares(numbers)

		p.mu.Lock()
		p.lastJobID = jobID
		p.lastSum = sum
		p.mu.Unlock()

		p.processed.Add(1)
		log.Printf("фоновая горутина обработала job=%d sum=%d", jobID, sum)
	}()

	return jobID
}

// wait блокируется до тех пор, пока все запущенные горутины не завершатся.
func (p *backgroundProcessor) wait() {
	p.wg.Wait()
}

func (p *backgroundProcessor) snapshot() statsResponse {
	p.mu.Lock()
	defer p.mu.Unlock()

	return statsResponse{
		ProcessedJobs: p.processed.Load(),
		LastJobID:     p.lastJobID,
		LastSum:       p.lastSum,
	}
}

// sumOfSquares возвращает сумму квадратов чисел.
func sumOfSquares(numbers []int64) int64 {
	var sum int64
	for _, n := range numbers {
		sum += n * n
	}
	return sum
}

func writeJSON(w http.ResponseWriter, statusCode int, payload any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(statusCode)
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("не удалось записать ответ: %v", err)
	}
}

func newMux(processor *backgroundProcessor) *http.ServeMux {
	mux := http.NewServeMux()

	mux.HandleFunc("POST /process", func(w http.ResponseWriter, r *http.Request) {
		var req processRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "некорректный JSON: "+err.Error(), http.StatusBadRequest)
			return
		}
		if len(req.Numbers) == 0 {
			http.Error(w, "поле numbers не должно быть пустым", http.StatusUnprocessableEntity)
			return
		}

		jobID := processor.submit(req.Numbers)
		writeJSON(w, http.StatusAccepted, processResponse{
			Status:   "accepted",
			JobID:    jobID,
			Accepted: len(req.Numbers),
		})
	})

	mux.HandleFunc("GET /stats", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, processor.snapshot())
	})

	return mux
}

func main() {
	processor := &backgroundProcessor{}
	server := &http.Server{
		Addr:              ":8080",
		Handler:           newMux(processor),
		ReadHeaderTimeout: 5 * time.Second,
	}

	// signal.NotifyContext без списка сигналов ловит любой сигнал остановки:
	// Ctrl+C и SIGTERM в терминале, SIGTERM от systemctl в Linux.
	ctx, stop := signal.NotifyContext(context.Background())
	defer stop()

	go func() {
		<-ctx.Done()
		log.Println("получен сигнал завершения, останавливаю сервер")

		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := server.Shutdown(shutdownCtx); err != nil {
			log.Printf("ошибка при остановке сервера: %v", err)
		}
	}()

	log.Printf("сервер слушает http://localhost%s", server.Addr)
	if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatalf("сервер не запустился: %v", err)
	}

	// Дожидаемся завершения фоновых горутин, чтобы не потерять результаты.
	processor.wait()
	log.Println("все фоновые горутины завершены, сервис остановлен")
}
