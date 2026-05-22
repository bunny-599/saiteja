.PHONY: install playwright dev clean

install:
	pip install -r requirements.txt
	cd frontend && npm install

playwright:
	playwright install chromium

dev:
	# Run both services concurrently
	# Note: On Windows, you can open two shells or run using concurrently node tool
	npx --yes concurrently --kill-others \
		"uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload" \
		"cd frontend && npm run dev"

clean:
	rm -rf backend/__pycache__ backend/scrapers/__pycache__ backend/ai/__pycache__ backend/utils/__pycache__ backend/services/__pycache__ backend/routers/__pycache__
	rm -rf frontend/node_modules frontend/dist
	rm -f sky_scrapper.db
