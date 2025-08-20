# Makefile for orchestrating the project components

.PHONY: crawl etl index up

crawl:
	@echo "Running web scraper..."
	python -m scraper.crawl

etl:
	@echo "Running ETL pipeline..."
	python -m pipeline.run

index: etl
	@echo "Building RAG vector index..."
	python -m rag.retriever.index

up:
	@echo "Bringing up all services with Docker Compose..."
	docker compose up

clean:
	@echo "Cleaning data artifacts..."
	rm -rf data/raw/* data/processed/*
	@echo "Cleaning up Docker containers..."
	docker compose down -v --remove-orphans