
clean:
	rm -rf build cleaner-build.zip
	rm -rf __pycache__

docker-build:
	docker-compose build

docker-run:
	docker-compose run lambda src/dbCleaner.main

build-lambda-package: clean
	mkdir build
	cp -r src build/.
	cp -r lib build/.
	pip install -r requirements.txt -t build/lib/.
	cd build; zip -9qr cleaner-build.zip .
	cp build/cleaner-build.zip .
	rm -rf build

