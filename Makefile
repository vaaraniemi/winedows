IMAGE ?= winedows-builder
DOCKER_RUN = docker run --rm --privileged -v $(CURDIR):/work -w /work $(IMAGE)

.PHONY: builder exes iso shell lint test guitest vm clean
builder:
	docker build -t $(IMAGE) .

exes: builder
	$(DOCKER_RUN) scripts/build-test-exes.sh

iso: builder exes
	$(DOCKER_RUN) scripts/build-iso.sh

shell: builder
	docker run --rm -it --privileged -v $(CURDIR):/work -w /work $(IMAGE) bash

lint:
	shellcheck -S warning scripts/*.sh build/auto/* build/config/hooks/live/* build/config/includes.chroot/usr/local/bin/*

test: builder
	$(DOCKER_RUN) scripts/smoke-test.sh

guitest: builder
	$(DOCKER_RUN) scripts/gui-test.sh

vm:
	scripts/run-qemu.sh

clean:
	rm -rf out build/.build build/cache build/chroot build/binary build/chroot.* build/binary.* build/live-image-*
