##############################################################
service=airenas/lium
version=0.1.0
########### DOCKER ##################################################################
tag=$(service):$(version)

dbuild:
	docker buildx build -t $(tag) --build-arg BUILD_VERSION=$(version) \
		-f Dockerfile ./
		
dpush: dbuild
	docker push $(tag)

dscan: dbuild
	docker scan --accept-license $(tag)	
#####################################################################################
.PHONY: dbuild dpush
